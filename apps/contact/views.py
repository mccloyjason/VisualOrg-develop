from django.conf import settings
from django.core.mail import send_mail
from rest_framework import mixins, viewsets

from .models import ContactFormEntry
from .serializers import ContactFormSerializer


class ContactFormViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    model = ContactFormEntry
    serializer_class = ContactFormSerializer

    def pre_save(self, obj):
        if self.request.user.is_authenticated():
            obj.user = self.request.user

    def post_save(self, obj, created=False):
        if created:
            subject = 'Contact Form <%s>' % obj.type
            body = obj.content
            sender = obj.user.email if obj.user else ''

            send_mail(subject, body, sender, settings.CONTACT_FORM_RECIPIENTS,
                      fail_silently=False)
