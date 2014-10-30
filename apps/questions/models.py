from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.timezone import now

from apps.accounts.models import Organization


class Question(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_datetime = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey(Organization, related_name='questions')
    question = models.TextField()
    open = models.BooleanField(default=True)
    closed_datetime = models.DateTimeField(null=True)
    approved = models.BooleanField(default=True)
    shared_users = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                          related_name='shared_questions')
    shared_organizations = models.ManyToManyField(Organization,
                                                  related_name='shared_questions')

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')

    def __unicode__(self):
        return self.question

    def save(self, *args, **kwargs):
        if not self.closed_datetime and not self.open:
            self.closed_datetime = now()
        return super(Question, self).save(*args, **kwargs)

    def user_has_permission(self, user):
        if self.created_by == user:
            return True
        if self.shared_users.filter(pk=user.pk).count() >= 1:
            return True
        if self.shared_organizations.filter(members__in=[user, ]).count() >= 1:
            return True

    @property
    def minutes_before_question_closed(self):
        """ Number of minutes before question was closed. """
        if not self.closed_datetime:
            return None
        time_to_close_delta = (self.closed_datetime - self.created_datetime)
        time_to_close = int(time_to_close_delta.total_seconds() / 60)
        return 0 if time_to_close < 0 else time_to_close


class Answer(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_datetime = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(Question, related_name='answers')
    content = models.TextField()

    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')

    def __unicode__(self):
        return self.content
