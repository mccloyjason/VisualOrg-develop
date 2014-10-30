from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.accounts.models import Organization
from apps.utils.mixins import VisibilityMixin, VISIBILTY_CHOICES

User = get_user_model()


class LiveDocument(models.Model, VisibilityMixin):
    title = models.CharField(_('Title'), max_length=50)
    created_by = models.ForeignKey(User)
    created_on = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey(Organization,
                                     related_name='live_documents')
    primary_organization = models.ForeignKey('accounts.Organization',
                                             related_name='all_live_documents')
    shared_with = models.ManyToManyField('accounts.User',
                                         related_name='shared_live_documents')
    visibility = models.CharField(_('Visibility'), choices=VISIBILTY_CHOICES,
                                  max_length=50)
    complete = models.BooleanField(default=False)
    completed_on = models.DateTimeField(null=True)
    reference_text = models.TextField()

    class Meta:
        verbose_name = _('Live document')
        verbose_name_plural = _('Live documents')

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.complete:
            self.completed_on = None
        elif not self.completed_on:
            self.completed_on = now()

        return super(LiveDocument, self).save(*args, **kwargs)


@receiver(pre_save, sender=LiveDocument)
def set_primary_org(sender, instance, **kwargs):
    try:
        instance.primary_organization
    except:
        instance.primary_organization = instance.organization.get_primary()


class LiveDocumentSection(models.Model):
    title = models.CharField(_('Title'), max_length=50)
    reference_text_start = models.PositiveIntegerField()
    reference_text_end = models.PositiveIntegerField()
    instructional_text = models.TextField()
    content = models.TextField()
    order = models.PositiveIntegerField()
    parent = models.ForeignKey(LiveDocument, related_name='sections')
    assigned_to = models.ForeignKey(User, null=True)

    class Meta:
        verbose_name = _('Live document section')
        verbose_name_plural = _('Live document sections')

    def __unicode__(self):
        return self.title


class LiveDocumentCompleteRecord(models.Model):
    live_document = models.ForeignKey(LiveDocument)
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Live document complete record')
        verbose_name_plural = _('Live document complete records')

    def __unicode__(self):
        return self.live_document


class DocumentManager(models.Manager):
    def filter_for_user(self, user):
        """ Return all documents user has access to. """
        query = Q(visibility=Document.PUBLIC) | \
            Q(visibility=Document.PRIVATE, created_by=user) | \
            Q(visibility=Document.ORG_ONLY,
              organization__memberships__user=user)

        if not user.external:
            query = query | Q(visibility=Document.ORG_ONLY_NO_EXTERNAL,
                              organization__memberships__user=user)

        return super(DocumentManager, self).get_query_set().filter(query) \
            .distinct()


class Document(models.Model):
    PUBLIC = 'public'
    PRIVATE = 'private'
    ORG_ONLY = 'org-only'
    ORG_ONLY_NO_EXTERNAL = 'org-only-no-external'
    VISIBILTY_CHOICES = (
        (PUBLIC, 'Public'),
        (PRIVATE, 'Private'),
        (ORG_ONLY, 'Organization only'),
        (ORG_ONLY_NO_EXTERNAL, 'Organization only (No external)'),
    )

    title = models.CharField(_('Title'), max_length=50)
    filetype = models.CharField(_('Filetype'), max_length=50)
    created_by = models.ForeignKey(User, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey(Organization, related_name='documents')
    visibility = models.CharField(_('Visibility'), choices=VISIBILTY_CHOICES,
                                  max_length=50)

    objects = DocumentManager()

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')

    def __unicode__(self):
        return self.title

    @property
    def current_version(self):
        """ Return latest version of document. """
        try:
            return self.versions.latest()
        except DocumentVersion.DoesNotExist:
            return None

    def get_current_file(self):
        versions = self.versions.all()
        if versions.count() == 0:
            return None
        return versions[0].file

    def user_has_access(self, user):
        """ Return true if user has access to the document. """
        if self.visibility == self.PUBLIC:
            return True
        elif self.visibility == self.PRIVATE and self.created_by == user:
            return True
        elif self.visibility in (self.ORG_ONLY, self.ORG_ONLY_NO_EXTERNAL):
            if user.external and self.visibility == self.ORG_ONLY_NO_EXTERNAL:
                return False
            elif self.organization.memberships.filter(user=user).count() >= 1:
                return True
        return False


class DocumentVersion(models.Model):
    document = models.ForeignKey(Document, related_name='versions')
    created_on = models.DateTimeField(auto_now_add=True)
    version = models.PositiveIntegerField()
    file = models.FileField(upload_to='documents/documentversion/file')

    class Meta:
        verbose_name = _('Document version')
        verbose_name_plural = _('Document versions')
        ordering = ('-version', )
        get_latest_by = 'created_on'
        unique_together = ('document', 'version')

    def __unicode__(self):
        return self.document

    def save(self, *args, **kwargs):
        if not self.version:
            # Increment version
            queryset = DocumentVersion.objects.filter(document=self.document)
            version = queryset.aggregate(models.Max('version'))['version__max']
            self.version = version + 1 if version else 1

        return super(DocumentVersion, self).save(*args, **kwargs)


class DocumentComment(models.Model):
    document = models.ForeignKey(Document, related_name='comments')
    author = models.ForeignKey(User, null=True)
    datetime = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    complete = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Document comment')
        verbose_name_plural = _('Document comments')

    def __unicode__(self):
        return self.content
