import uuid
from copy import copy
from datetime import timedelta
from mptt.models import MPTTModel, TreeForeignKey
from django.core.mail import EmailMessage
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from django.db import connection
from django.db.models import Avg, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template import Context
from django.template import loader
from django.contrib.sites.models import Site
from django.shortcuts import render


from custom_user.models import AbstractEmailUser, EmailUserManager


class UserManager(EmailUserManager):
    def visible_members(self):
        return super(UserManager, self).get_query_set() \
            .exclude(organization_memberships__hidden=True)


class User(AbstractEmailUser):
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    external = models.BooleanField(default=False)
    activated = models.BooleanField(default=False)
    reset_password_code = models.CharField(max_length=40, null=True)
    validation_code = models.CharField(max_length=40, null=True)

    objects = UserManager()

    def __unicode__(self):
        return self.email

    def get_primary_org(self):
        try:
            return self.organizations.get(parent__isnull=True)
        except Organization.DoesNotExist:
            return None

    @property
    def is_active(self):
        return self.activated

    @is_active.setter
    def is_active(self, value):
        self.activated = value

    def initiate_reset_password_process(self):
        """ Set reset_password_code and email a token to the user. """
        token = uuid.uuid4().hex[:6]
        self.reset_password_code = token
        self.save()

        message = 'Your token is: %s' % token
        send_mail('Reset Password', message, settings.SUPPORT_EMAIL,
                  [self.email, ], fail_silently=False)

    def add_to_organization(self, organization, admin_level):
        """ Add user to organization. """
        member = OrganizationMembership(user=self, organization=organization,
                                        administrative_level=admin_level)
        member.save()

    def get_statistics(self, organization):
        """ Get a dict with statistics for output. """
        fields = ('num_processes_developed', 'num_processes_initiated')
        truncate_date = connection.ops.date_trunc_sql('month', 'date')
        qs = self.userstatistic_set.filter(organization=organization)
        qs = qs.extra({'month': truncate_date})

        avgs = dict({(i, Sum(i)) for i in fields})
        monthly = qs.values('month').annotate(**avgs).order_by('-month')[:12]
        for month in monthly:
            month['month'] = '-'.join([str(month['month'].year),
                                       str(month['month'].month)])

        return {'stats_by_month': monthly}

    def send_password(self):
        site=Site.objects.get_current()
        password=self.password
        email=self.email
        firstname=self.first_name
        lastname=self.last_name
        template=loader.get_template('mails/user_password.html')
        c=Context({'site':site,'email':email,'password':password,'firstname':firstname,'lastname':lastname,})
        content=template.render(c)
        email=EmailMessage('[%s]%s'%(site.name,'Visual Org'),content,settings.DEFAULT_FROM_EMAIL,[email],[], headers = {})
        email.content_subtype='html'
        email.send()

#    def save(self,*args,**kwargs):
#        super(User, self).save(*args, **kwargs)
#        self.send_password()


class Role(MPTTModel):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey('Organization', related_name='roles')
    parent = TreeForeignKey('self', blank=True, null=True,
                            related_name="children")
    related_to = models.ManyToManyField('self',null=True,blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='roles',
                             null=True)

    def __unicode__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Role, self).__init__(*args, **kwargs)
        self.user_cached = copy(self.user) if self.pk else None

    def save(self, *args, **kwargs):
        obj = super(Role, self).save(*args, **kwargs)

        ## NOTE: Log to MoveRoleRecord.
        if self.user_cached != self.user:
            if self.user_cached:
                MoveRoleRecord.objects.create(user=self.user_cached,
                                              from_role=self)
            if self.user:
                MoveRoleRecord.objects.create(user=self.user, to_role=self)

        self.user_cached = copy(self.user)
        return obj


class MoveRoleRecord(models.Model):
    from_role = models.ForeignKey(Role, blank=True, null=True,
                                  related_name='from_move_role_records')
    to_role = models.ForeignKey(Role, blank=True, null=True,
                                related_name='to_move_role_records')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='move_role_records')
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'datetime'


class LoginRecord(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='login_records')

    def __unicode__(self):
        return u'%s' %(self.user)


class Organization(MPTTModel):
    STRUCTURAL = 'structural'
    WORKGROUP = 'workgroup'
    ORGANIZATION_TYPE_CHOICES = (
        (STRUCTURAL, 'Structural'),
        (WORKGROUP, 'Workgroup'),
    )

    name = models.CharField(max_length=100)
    parent = TreeForeignKey('self', null=True,blank=True,related_name='children')
    type = models.CharField(max_length=30, choices=ORGANIZATION_TYPE_CHOICES)
    payment_plan = models.ForeignKey('billing.PaymentPlan', null=True,
                                     related_name='organizations')
    billing_contact = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                                        related_name='organizations_billing')
    trial_start = models.DateTimeField(null=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                     through='OrganizationMembership',
                                     related_name='organizations')

    def __unicode__(self):
        return unicode(self.name)

    def get_primary(self):
        org = self
        while org.parent is not None:
            org = org.parent
        return org

    @property
    def is_primary(self):
        return not self.parent

    @property
    def visible_members(self):
        pks = [m.user.pk for m in self.memberships.filter(hidden=False)]
        return User.objects.filter(pk__in=pks)

    def user_is_administrative(self, user):
        """ True if user is a Superuser, Administrator or Supervisor. """
        return self.memberships.filter(**{
            'user': user,
            'administrative_level__in': (OrganizationMembership.SUPERUSER,
                                         OrganizationMembership.ADMINISTRATOR,
                                         OrganizationMembership.SUPERVISOR),
        }).count() >= 1

    def get_statistics(self):
        """ Get a dict with statistics for output. """
        avg_fields = ('num_roles', 'num_roles_filled', 'num_roles_unfilled',
                      'num_external_roles', 'num_teams', 'num_workgroups',
                      'num_documents', 'num_documents_static',
                      'num_livedocs_active',
                      'average_time_questions_open')
        sum_fields = ('num_livedocs_completed', 'num_questions', 'num_answers')

        truncate_date = connection.ops.date_trunc_sql('month', 'date')
        qs = self.organizationstatistic_set.extra({'month': truncate_date})

        fields = dict({(i, Avg(i)) for i in avg_fields})
        fields.update(dict({(i, Sum(i)) for i in sum_fields}))

        monthly = qs.values('month').annotate(**fields).order_by('-month')[:12]
        for month in monthly:
            month['month'] = '-'.join([str(month['month'].year),
                                       str(month['month'].month)])
            for field in fields:
                month[field] = round(month[field], 2)

        # NOTE: Role succession data
        role_succession = []
        start_datetime = now() - timedelta(days=30)
        root_roles = Role.objects.root_nodes().filter(organization=self)
        for role in root_roles:
            roles = role.get_descendants(include_self=True)
            count = MoveRoleRecord.objects.filter(
                to_role__in=roles, datetime__gte=start_datetime).count()
            if count > 0:
                role_succession.append([role.name, count])

        return {
            'stats_by_month': monthly,
            'role_succession': role_succession,
        }


@receiver(post_save, sender=Organization)
def create_settings(sender, instance, created, **kwargs):
    if created:
        OrganizationSettings.objects.create(organization=instance)


class OrganizationMembership(models.Model):
    SUPERUSER = 'superuser'
    ADMINISTRATOR = 'administrator'
    SUPERVISOR = 'supervisor'
    USER = 'user'
    ADMINISTRATIVE_CHOICES = (
        (SUPERUSER, 'Superuser'),
        (ADMINISTRATOR, 'Administrator'),
        (SUPERVISOR, 'Supervisor'),
        (USER, 'User'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='organization_memberships')
    organization = models.ForeignKey(Organization, related_name='memberships')
    hidden = models.BooleanField(default=False)
    administrative_level = models.CharField(max_length=30,
                                            choices=ADMINISTRATIVE_CHOICES)

    class Meta:
        unique_together = ('user', 'organization')


class OrganizationSettings(models.Model):
    DOC_VISIBILITY_CHOICES = (
        ('all', 'All'),
        ('within_org', 'Within Organization'),
        ('within_org_exc_external', 'Within Organization, Excluding External'),
    )
    LIVEDOC_VISIBILITY_CHOICES = (
        ('all', 'All'),
        ('primary_org', 'Primary Organization'),
        ('org_only', 'Organization Only'),
        ('private', 'Private'),
    )
    PROCESS_CREATION_CHOICES = (
        ('restricted', 'Restricted'),
        ('all', 'All'),
        ('all_exc_external', 'All, Except External'),
    )
    PROCESS_EDITING_CHOICES = (
        ('restricted', 'Restricted'),
        ('all', 'All'),
        ('all_exc_external', 'All, Except External'),
    )
    PROCESS_VIEWING_CHOICES = (
        ('restricted', 'Restricted'),
        ('all', 'All'),
        ('all_exc_external', 'All, Except External'),
    )
    QA_CONFIGURATION_CHOICES = (
        ('open', 'Open'),
        ('administered', 'Administered'),
    )
    DEFAULT_ORG_VIEW_CHOICES = (
        ('visual', 'Visual'),
        ('list', 'List'),
    )

    organization = models.OneToOneField(Organization)
    document_visibility = models.CharField(max_length=30,
                                           choices=DOC_VISIBILITY_CHOICES,
                                           default='all')
    org_hierarchy_visibility = models.PositiveIntegerField(default=2)
    livedoc_visibility = models.CharField(max_length=30,
                                          choices=LIVEDOC_VISIBILITY_CHOICES,
                                          default='all')
    process_creation = models.CharField(max_length=30,
                                        choices=PROCESS_CREATION_CHOICES,
                                        default='all')
    process_editing = models.CharField(max_length=30,
                                       choices=PROCESS_EDITING_CHOICES,
                                       default='all')
    process_viewing = models.CharField(max_length=30,
                                       choices=PROCESS_VIEWING_CHOICES,
                                       default='all')
    qa_configuration = models.CharField(max_length=30,
                                        choices=QA_CONFIGURATION_CHOICES,
                                        default='open')
    default_org_view = models.CharField(max_length=30,
                                        choices=DEFAULT_ORG_VIEW_CHOICES,
                                        default='visual')

    class Meta:
        verbose_name=('Organisation Settings')
        verbose_name_plural=('Organisation Settings')

    def __unicode__(self):
        return u'%s' %(self.organization)


class OrganizationStatistic(models.Model):
    """ Stats for an organization. """
    date = models.DateField()
    organization = models.ForeignKey(Organization)

    num_roles = models.PositiveIntegerField(default=0)
    num_roles_filled = models.PositiveIntegerField(default=0)
    num_roles_unfilled = models.PositiveIntegerField(default=0)
    num_external_roles = models.PositiveIntegerField(default=0)

    num_teams = models.PositiveIntegerField(default=0)
    num_workgroups = models.PositiveIntegerField(default=0)

    num_livedocs_active = models.PositiveIntegerField(default=0)
    num_livedocs_completed = models.PositiveIntegerField(default=0)

    num_documents = models.PositiveIntegerField(default=0)
    num_documents_static = models.PositiveIntegerField(default=0)

    average_time_questions_open = models.PositiveIntegerField(default=0)
    num_questions = models.PositiveIntegerField(default=0)
    num_answers = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Organization statistic')
        verbose_name_plural = _('Organization statistics')
        unique_together = ('date', 'organization')
        get_latest_by = 'date'

    def __unicode__(self):
        return self.date


class UserStatistic(models.Model):
    """ Stats for a user. """
    date = models.DateField()
    user = models.ForeignKey(User)
    organization = models.ForeignKey(Organization)

    num_processes_developed = models.PositiveIntegerField(default=0)
    num_processes_initiated = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('User statistic')
        verbose_name_plural = _('User statistics')
        unique_together = ('date', 'user')
        get_latest_by = 'date'

    def __unicode__(self):
        return self.date
