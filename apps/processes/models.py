from django.db import models
from django.utils.translation import ugettext as _
from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.utils.mixins import VisibilityMixin, VISIBILTY_CHOICES


class Process(models.Model, VisibilityMixin):
    """A connected series of tasks."""
    title = models.CharField(max_length=255)
    organization = models.ForeignKey('accounts.Organization',
                                     related_name='processes')
    primary_organization = models.ForeignKey('accounts.Organization',
                                             related_name='all_processes')
    shared_with = models.ManyToManyField('accounts.User',
                                         related_name='shared_processes')
    created_datetime = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.User',
                                   related_name='created_processes',
                                   null=True)
    visibility = models.CharField(_('Visibility'), choices=VISIBILTY_CHOICES,
                                  max_length=50)

    def __unicode__(self):
        return unicode(self.title)

    class Meta:
        verbose_name=('Process')
        verbose_name_plural=('Process')


@receiver(pre_save, sender=Process)
def set_primary_org(sender, instance, **kwargs):
    try:
        instance.primary_organization
    except:
        instance.primary_organization = instance.organization.get_primary()


class ProcessInstance(models.Model, VisibilityMixin):
    """An instantiation of a Process."""
    process = models.ForeignKey('Process', related_name="instances")
    initiated_by = models.ForeignKey('accounts.User')
    start_datetime = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_on = models.DateTimeField(null=True)
    visibility = models.CharField(_('Visibility'), choices=VISIBILTY_CHOICES,
                                  max_length=50)
    organization = models.ForeignKey('accounts.Organization',
                                     related_name='process_instances')
    primary_organization = models.ForeignKey('accounts.Organization',
                                             related_name='all_process_instances')
    shared_with = models.ManyToManyField('accounts.User',
                                         related_name='shared_process_instances')

    def __unicode__(self):
        return unicode("Instance {}: {}".format(self.pk, self.process))


@receiver(pre_save, sender=ProcessInstance)
def set_primary_org_instance(sender, instance, **kwargs):
    try:
        instance.primary_organization
    except:
        instance.primary_organization = instance.organization.get_primary()


class ProcessStep(models.Model):
    """A step in a process."""
    title = models.CharField(max_length=255)
    parent = models.ForeignKey('Process', related_name='steps')
    root = models.BooleanField(default=False)
    description = models.TextField()
    process_type = models.ForeignKey('ProcessType', related_name="+")
    role = models.ForeignKey('accounts.Role', related_name="processes")
    next_nodes = models.ManyToManyField('ProcessStep', related_name='+')

    def __unicode__(self):
        return unicode(self.title)


class ProcessStepAssignment(models.Model):
    """An assignment of a step to a user."""
    instance = models.ForeignKey('ProcessInstance', related_name="assignments")
    step = models.OneToOneField('ProcessStep', related_name='assignment')
    assigned_user = models.ForeignKey('accounts.User',
                                      related_name='assignments')
    amount_completed = models.FloatField(default=0)
    completed = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(
            "User: {}; Step: {}".format(self.assigned_user, self.step))


class ProcessType(models.Model):
    """A type of process step."""
    name = models.CharField(max_length=255)
    shape = models.ImageField(upload_to="process_widgets")

    def __unicode__(self):
        return unicode(self.name)


class ProcessStepTask(models.Model):
    """An subdivision of a step."""
    FREQUENCY_ONCE = 'once'
    FREQUENCY_HOURLY = 'hourly'
    FREQUENCY_DAILY = 'daily'
    FREQUENCY_WEEKLY = 'weekly'
    FREQUENCY_BIWEEKLY = 'biweekly'
    FREQUENCY_MONTHLY = 'monthly'
    FREQUENCY_QUARTERLY = 'quarterly'
    FREQUENCY_MIDYEAR = 'midyear'
    FREQUENCY_ANNUALLY = 'annually'
    FREQUENCY_CHOICES = (
        (FREQUENCY_ONCE, 'Once'), (FREQUENCY_HOURLY, 'Hourly'),
        (FREQUENCY_DAILY, 'Daily'), (FREQUENCY_WEEKLY, 'Weekly'),
        (FREQUENCY_BIWEEKLY, 'Biweekly'), (FREQUENCY_MONTHLY, 'Monthly'),
        (FREQUENCY_QUARTERLY, 'Quarterly'), (FREQUENCY_MIDYEAR, 'Midyear'),
        (FREQUENCY_ANNUALLY, 'Annually')
    )

    title = models.CharField(max_length=255)
    parent = models.ForeignKey('ProcessStep', related_name='tasks')
    criticality = models.PositiveIntegerField()
    order = models.PositiveIntegerField()
    frequency = models.CharField(max_length=255, choices=FREQUENCY_CHOICES)
    description = models.TextField()
    document = models.ForeignKey('documents.Document', null=True, blank=True)

    def __unicode__(self):
        return unicode(self.title)
