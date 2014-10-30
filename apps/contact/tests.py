from mock import Mock
from django.core import mail
from django_nose import FastFixtureTestCase as TestCase

from .views import ContactFormViewSet


class ContactFormViewSetTest(TestCase):
    def test_contactviewset_user_set(self):
        """ Validate obj.user is set if user is authenticated. """
        view = ContactFormViewSet()
        view.request = Mock()
        view.request.user.is_authenticated = Mock(return_value=True)

        obj = Mock()
        view.pre_save(obj)

        self.assertEqual(obj.user, view.request.user)
        view.request.user.is_authenticated.assert_called_with_once()

    def test_contactviewset_email_sent(self):
        """ Validate email is sent. """
        view = ContactFormViewSet()
        view.request = Mock()

        obj = Mock()
        obj.type = 'MessageType'
        obj.content = 'Message content'
        view.post_save(obj, created=True)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('MessageType', mail.outbox[0].subject)
        self.assertEqual('Message content', mail.outbox[0].body)
