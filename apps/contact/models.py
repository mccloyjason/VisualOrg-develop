from django.db import models
from django.conf import settings


class ContactFormEntry(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=30)
    content = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                             related_name='contact_form_entries')

    def __unicode__(self):
        return u"%s"%(self.user)

    class Meta:
        verbose_name=('Contact form entries')
        verbose_name_plural=('Contact form entries')
