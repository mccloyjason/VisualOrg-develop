from mock import Mock
from django_nose import FastFixtureTestCase as TestCase
from django.contrib.auth import get_user_model

from apps.accounts.models import Organization, OrganizationMembership

from .models import Question
from .serializers import QuestionSerializer, CondensedQuestionSerializer
from .views import (QuestionViewSet, AnswerViewSet, IsQuestionCreatorOrShared,
                    IsQuestionCreator, IsCreatorAndQuestionOpenOrReadOnly)

User = get_user_model()


class QuestionSerializerTest(TestCase):
    def test_question_attributes_transformed(self):
        """
        Test question organization, shared_users and shared_organizations
        attributes are transformed.
        """
        ## Test without instance
        data = QuestionSerializer(None).data
        self.assertIsNone(data['organization'])
        self.assertIsNone(data['shared_users'])
        self.assertIsNone(data['shared_organizations'])

        # Test with instance
        org = Organization.objects.create()
        user = User.objects.create()
        question = Question.objects.create(organization=org, created_by=user,
                                           question='The question!')
        question.shared_users.add(user)
        question.shared_organizations.add(org)

        data = QuestionSerializer(question).data
        self.assertIn('id', data['organization'].keys())
        self.assertIn('id', data['shared_users'][0].keys())
        self.assertIn('id', data['shared_organizations'][0].keys())


class IsQuestionCreatorOrSharedTest(TestCase):
    def setUp(self):
        org = Organization.objects.create()
        self.good_user = User.objects.create(email='good@example.com')
        self.bad_user = User.objects.create(email='bad@example.com')
        self.shared_user = User.objects.create(email='shared@example.com')
        self.question = Question.objects.create(organization=org,
                                                created_by=self.good_user,
                                                question='The question!')
        self.answer = self.question.answers.create(created_by=self.good_user,
                                                   content='An answer!')

    def test_creator_permission(self):
        """ Test creator has access. """
        permission = IsQuestionCreatorOrShared()

        request = Mock(user=self.bad_user)
        self.assertFalse(permission.has_object_permission(request, None,
                                                          self.question))
        self.assertFalse(permission.has_object_permission(request, None,
                                                          self.answer))

        request = Mock(user=self.good_user)
        self.assertTrue(permission.has_object_permission(request, None,
                                                         self.question))
        self.assertTrue(permission.has_object_permission(request, None,
                                                         self.answer))

    def test_shared_user_permission(self):
        """ Test shared_users has access. """
        permission = IsQuestionCreatorOrShared()
        request = Mock(user=self.shared_user)

        self.assertFalse(permission.has_object_permission(request, None,
                                                          self.question))
        self.assertFalse(permission.has_object_permission(request, None,
                                                          self.answer))

        self.question.shared_users.add(self.shared_user)
        self.assertTrue(permission.has_object_permission(request, None,
                                                         self.question))
        self.assertTrue(permission.has_object_permission(request, None,
                                                         self.answer))

    def test_shared_organizations_permission(self):
        """ Test shared_organizations has access. """
        permission = IsQuestionCreatorOrShared()
        request = Mock(user=self.shared_user)

        self.assertFalse(permission.has_object_permission(request, None,
                                                          self.question))
        self.assertFalse(permission.has_object_permission(request, None,
                                                          self.answer))

        shared_org = Organization.objects.create()
        OrganizationMembership(user=self.shared_user, organization=shared_org,
                               administrative_level='superuser').save()
        self.question.shared_organizations.add(shared_org)
        self.assertTrue(permission.has_object_permission(request, None,
                                                         self.question))
        self.assertTrue(permission.has_object_permission(request, None,
                                                         self.answer))


class IsCreatorAndQuestionOpenOrReadOnlyTest(TestCase):
    def setUp(self):
        org = Organization.objects.create()
        self.good_user = User.objects.create(email='good@example.com')
        self.bad_user = User.objects.create(email='bad@example.com')
        self.question = Question.objects.create(organization=org,
                                                created_by=self.good_user,
                                                question='The question!')
        self.answer = self.question.answers.create(created_by=self.good_user,
                                                   content='An answer!')

    def test_creator_permission(self):
        """ Test creator can post. """
        permission = IsCreatorAndQuestionOpenOrReadOnly()

        request = Mock(user=self.bad_user, method='POST')
        self.assertFalse(permission.has_object_permission(request, None,
                                                          self.question))
        self.assertFalse(permission.has_object_permission(request, None,
                                                          self.answer))

        request = Mock(user=self.good_user, method='POST')
        self.assertTrue(permission.has_object_permission(request, None,
                                                         self.question))
        self.assertTrue(permission.has_object_permission(request, None,
                                                         self.answer))

    def test_open_permission(self):
        """ Test creator can not post if quextion is not open. """
        permission = IsCreatorAndQuestionOpenOrReadOnly()

        request = Mock(user=self.good_user, method='POST')
        self.assertTrue(permission.has_object_permission(request, None,
                                                         self.question))
        self.assertTrue(permission.has_object_permission(request, None,
                                                         self.answer))

        self.question.open = False
        self.question.save()
        request = Mock(user=self.good_user, method='POST')
        self.assertFalse(permission.has_object_permission(request, None,
                                                          self.question))
        self.assertFalse(permission.has_object_permission(request, None,
                                                          self.answer))

    def test_read_only_permission(self):
        """ Test anyone can read. """
        permission = IsCreatorAndQuestionOpenOrReadOnly()

        request = Mock(user=self.bad_user, method='GET')
        self.assertTrue(permission.has_object_permission(request, None,
                                                         self.question))
        self.assertTrue(permission.has_object_permission(request, None,
                                                         self.answer))


class IsQuestionCreatorTest(TestCase):
    def setUp(self):
        org = Organization.objects.create()
        self.good_user = User.objects.create(email='good@example.com')
        self.bad_user = User.objects.create(email='bad@example.com')
        self.question = Question.objects.create(organization=org,
                                                created_by=self.good_user,
                                                question='The question!')

    def test_permission(self):
        """ Test user with access to question can access answers. """
        permission = IsQuestionCreator()
        view = Mock(kwargs={'question': self.question.pk})

        request = Mock(user=self.bad_user)
        self.assertFalse(permission.has_permission(request, view))

        request = Mock(user=self.good_user)
        self.assertTrue(permission.has_permission(request, view))


class QuestionViewSetTest(TestCase):
    def test_get_serializer_class(self):
        """ Test CondensedQuestionSerializer is used for root API. """
        view = QuestionViewSet()

        view.request = Mock(method='GET')
        view.kwargs = {}
        self.assertEqual(view.get_serializer_class(),
                         CondensedQuestionSerializer)

        view.request = Mock(method='POST')
        view.kwargs = {}
        self.assertEqual(view.get_serializer_class(), QuestionSerializer)

        view.request = Mock(method='GET')
        view.kwargs = {'pk': 100}
        self.assertEqual(view.get_serializer_class(), QuestionSerializer)

        view.request = Mock(method='PUT')
        view.kwargs = {'pk': 100}
        self.assertEqual(view.get_serializer_class(), QuestionSerializer)

    def test_get_queryset(self):
        """ Test only questions shared with user returned. """
        org = Organization.objects.create()
        creator = User.objects.create(email='creator@example.com')
        shared_user = User.objects.create(email='shared@example.com')
        question = Question.objects.create(organization=org,
                                           created_by=creator,
                                           question='The question!')

        view = QuestionViewSet()
        view.kwargs = {}
        view.request = Mock(user=shared_user, GET={'organization': org.pk})

        questions = view.get_queryset()
        self.assertEqual(len(questions), 0)

        OrganizationMembership(user=shared_user, organization=org,
                               administrative_level='superuser').save()
        question.shared_organizations.add(org)

        questions = view.get_queryset()
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].question, 'The question!')

        question.shared_organizations.clear()
        question.shared_users.add(shared_user)

        questions = view.get_queryset()
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].question, 'The question!')

    def test_pre_save(self):
        """ Test Question.created_by is set to authenticated user. """
        obj = Mock(created_by_id=None)
        view = QuestionViewSet()
        view.request = Mock(user='Authenticated user')
        view.pre_save(obj)
        self.assertEqual(obj.created_by, 'Authenticated user')


class AnswerViewSetTest(TestCase):
    def test_pre_save(self):
        """ Test created_by and question is set when creating object. """
        org = Organization.objects.create()
        creator = User.objects.create(email='creator@example.com')
        question = Question.objects.create(organization=org,
                                           created_by=creator,
                                           question='The question!')

        obj = Mock(created_by_id=None, question_id=None)
        view = AnswerViewSet()
        view.kwargs = {'question': question.pk}
        view.request = Mock(user='Authenticated user')
        view.pre_save(obj)
        self.assertEqual(obj.created_by, 'Authenticated user')
