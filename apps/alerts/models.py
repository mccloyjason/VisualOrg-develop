from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


class Alert(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  related_name='alerts')
    content = models.TextField()
    viewed = models.BooleanField(default=False)
    reference_id = models.PositiveIntegerField()
    reference_type = models.ForeignKey(ContentType)
    reference = generic.GenericForeignKey('reference_type', 'reference_id')

    class Meta:
        verbose_name = _('Alert')
        verbose_name_plural = _('Alerts')

    def __unicode__(self):
        return self.content
