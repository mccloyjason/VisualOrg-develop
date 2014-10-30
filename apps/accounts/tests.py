from mock import Mock
from datetime import datetime, timedelta

from django_nose import FastFixtureTestCase as TestCase
from django.core import mail
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware

from rest_framework.test import APIRequestFactory

from apps.billing.models import PaymentPlan

from .models import (Organization, OrganizationMembership, Role,
                     MoveRoleRecord, OrganizationStatistic, UserStatistic)
from .views import (RegisterViewSet, LoginViewSet, PasswordForgotViewSet,
                    PasswordResetViewSet, ValidateUserViewSet,
                    OrganizationViewSet, RoleViewSet, IsInOrganization,
                    IsOrganizationSuperOrAdminOrReadOnly, MembershipViewSet,
                    ModifyUserPermission, UserViewSet)
from .serializers import (UserSerializer, RegisterSerializer,
                          UserInputSerializer, CreateOrganizationSerializer,
                          CondensedOrganizationSerializer, RoleSerializer,
                          OrganizationSerializer,
                          OrganizationMembershipSerializer,
                          UserOrganizationMembershipSerializer,
                          CreateUserSerializer, UpdateUserSerializer)

User = get_user_model()
request_factory = APIRequestFactory()


def add_session_to_request(request):
    """Annotate a request object with a session"""
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()


class RegisterSerializerTest(TestCase):
    def test_user_created(self):
        """
        Test user object created.
        """
        data = {
            'email': 'user@example.com',
            'first_name': 'FName',
            'last_name': 'LName',
            'organization_name': 'Org Name',
            'password': 'passwd',
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertEqual(user.first_name, 'FName')
        self.assertEqual(user.last_name, 'LName')
        self.assertEqual(user.organization_name, 'Org Name')
        self.assertIn('pbkdf2_sha256$', user.password)

    def test_validate_email(self):
        """
        Test the same email can not be used twice.
        """
        data = {
            'email': 'user@example.com',
            'first_name': 'FName',
            'last_name': 'LName',
            'organization_name': 'Org Name',
            'password': 'passwd',
        }
        User.objects.create(email=data['email'])
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('User with this Email address already exists.',
                      serializer.errors['email'])


class RegisterUserViewTest(TestCase):
    def test_get_serializer_class(self):
        """
        Test RegisterSerializer is used when no user instance is given.
        """
        view = RegisterViewSet()
        self.assertEqual(view.get_serializer_class(), RegisterSerializer)
        self.assertEqual(view.get_serializer_class(instance=True),
                         UserSerializer)

    def test_post_save(self):
        """
        Test PaymentPlan, Organization and membership are created. + Email sent
        """
        PaymentPlan.objects.create(monthly_cost=0, max_users=100)
        view = RegisterViewSet()
        user = User.objects.create()
        user.organization_name = 'Org Name'
        user.validation_code = 'validation-code'

        view.post_save(user, created=True)

        self.assertEqual(len(user.organizations.all()), 1)
        self.assertEqual(user.organizations.all()[0].name, 'Org Name')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Complete your registration', mail.outbox[0].subject)
        self.assertIn('validation-code', mail.outbox[0].body)


class LoginTest(TestCase):
    def test_login_api(self):
        """ Test LoginViewSet. """
        data = {
            'email': 'user@example.com',
            'password': 'passwd',
        }
        view = LoginViewSet.as_view({'post': 'create'})
        request = request_factory.post('/', data)
        add_session_to_request(request)

        # Test with invalid credentials.
        response = view(request)
        response.render()
        self.assertIn('Login invalid', response.content)
        self.assertEqual(response.status_code, 403)

        # Test with valid credentials but inactive.
        user = User.objects.create(email=data['email'])
        user.set_password(data['password'])
        user.save()

        response = view(request)
        response.render()
        self.assertIn('Inactive user', response.content)
        self.assertEqual(response.status_code, 403)

        # Test with valid credentials and active.
        user.activated = True
        user.save()

        response = view(request)
        response.render()
        self.assertIn(user.email, response.content)
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(email=data['email'])
        self.assertTrue(user.activated)
        self.assertIsNone(user.validation_code)


class ValidateUserTest(TestCase):
    def test_validate_user_api(self):
        """ Test ValidateUserViewSet. """
        data = {
            'email': 'user@example.com',
            'code': 'validate-code',
        }
        view = ValidateUserViewSet.as_view({'post': 'create'})
        request = request_factory.post('/', data)

        # Test when user with code does not exist.
        response = view(request)
        response.render()
        self.assertIn('Invalid code', response.content)
        self.assertEqual(response.status_code, 403)

        # Test when user with code exists.
        User.objects.create(email=data['email'],
                            validation_code='validate-code')
        response = view(request)
        response.render()
        self.assertIn('Account verified.', response.content)
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(email=data['email'])
        self.assertTrue(user.activated)
        self.assertIsNone(user.validation_code)


class ForgottenPasswordTest(TestCase):
    def test_forgotten_password_api(self):
        """ Test PasswordForgotViewSet. """
        data = {
            'email': 'user@example.com',
        }
        view = PasswordForgotViewSet.as_view({'post': 'create'})
        request = request_factory.post('/', data)

        # Test when user does not exist.
        response = view(request)
        response.render()
        self.assertIn('Request processed', response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

        # Test when user exists.
        User.objects.create(email=data['email'])
        response = view(request)
        response.render()
        self.assertIn('Request processed', response.content)
        self.assertEqual(response.status_code, 200)

        # Test email is sent
        user = User.objects.get(email=data['email'])
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Reset Password', mail.outbox[0].subject)
        self.assertIn(user.reset_password_code, mail.outbox[0].body)
        self.assertTrue(len(user.reset_password_code) == 6)

    def test_reset_password_api(self):
        """ Test PasswordResetViewSet. """
        data = {
            'email': 'user@example.com',
            'code': 'reset-code',
            'password': 'passwd',
        }
        view = PasswordResetViewSet.as_view({'post': 'create'})
        request = request_factory.post('/', data)

        # Test when user with code does not exist.
        response = view(request)
        response.render()
        self.assertIn('Invalid code', response.content)
        self.assertEqual(response.status_code, 403)

        # Test when user with code exists.
        User.objects.create(email=data['email'],
                            reset_password_code='reset-code')
        response = view(request)
        response.render()
        self.assertIn('Password reset', response.content)
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(email=data['email'])
        self.assertIn('pbkdf2_sha256$', user.password)
        self.assertIsNone(user.reset_password_code)


class UserModelTestCase(TestCase):
    def test_get_statistics_month(self):
        """ Validate get_statistics() 'stats_by_month' output. """
        user = User.objects.create()
        organization = Organization.objects.create()
        for i in range(0, 10):
            date = datetime(2012, 12, 30) - timedelta(days=i)
            UserStatistic.objects.create(
                user=user, organization=organization, date=date,
                num_processes_developed=100, num_processes_initiated=101)

        data = user.get_statistics(organization)
        stats = data['stats_by_month'][0]
        self.assertEqual(stats['num_processes_developed'], 1000.0)
        self.assertEqual(stats['num_processes_initiated'], 1010.0)


class OrganizationViewSetTest(TestCase):
    def test_get_serializer_class(self):
        """ Test correct serializer is used. """
        view = OrganizationViewSet(kwargs={})
        view.request = Mock()

        view.request.method = 'GET'
        self.assertEqual(view.get_serializer_class(),
                         CondensedOrganizationSerializer)

        view.request.method = 'POST'
        self.assertEqual(view.get_serializer_class(),
                         CreateOrganizationSerializer)

        org = Organization.objects.create()
        view.request.method = 'GET'
        view.kwargs['pk'] = org.pk
        self.assertEqual(view.get_serializer_class(instance=org),
                         OrganizationSerializer)

    def test_get_queryset(self):
        """ Test only organizations where user is a member are returned. """
        user = User.objects.create()
        org = Organization.objects.create(name='Org 1', type='structural')
        OrganizationMembership.objects.create(user=user, organization=org)
        Organization.objects.create(name='Org 2', type='structural')

        view = OrganizationViewSet(kwargs={})
        view.request = Mock(user=user)

        orgs = view.get_queryset()
        self.assertEqual(len(orgs), 1)
        self.assertEqual(orgs[0].name, 'Org 1')

    def test_post_save(self):
        """ Test memberships are created. """
        user1_pk = User.objects.create(email='one@example.com',
                                       first_name='Name one').pk
        user2_pk = User.objects.create(email='two@example.com').pk
        users_data = [{'pk': user1_pk, 'status': 'hidden'},
                      {'pk': user2_pk, 'status': 'structural'}]

        org = Organization.objects.create()
        org.new_users = users_data

        view = OrganizationViewSet()
        view.post_save(org, created=True)

        members = org.memberships.all()
        self.assertEqual(len(members), 2)
        self.assertEqual(members[0].user.first_name, 'Name one')
        self.assertEqual(members[0].hidden, True)
        self.assertEqual(members[0].administrative_level, '')
        self.assertEqual(members[1].hidden, False)
        self.assertEqual(members[1].administrative_level, 'structural')


class UserInputSerializerTest(TestCase):
    def test_user_created(self):
        """ Test user object created. """
        data = {
            'pk': '1',
            'status': 'hidden',
        }
        serializer = UserInputSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('User with pk 1 does not exist.',
                      serializer.errors['pk'])

        data['pk'] = User.objects.create().pk
        serializer = UserInputSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.data['pk'], data['pk'])


class CreateOrganizationSerializerTest(TestCase):
    def test_organisation_created(self):
        """ Test organisation object created. """
        user_pk = User.objects.create().pk
        org_pk = Organization.objects.create().pk
        users_data = [{'pk': user_pk, 'status': 'hidden'}]
        data = {
            'parent': org_pk,
            'name': 'New org name',
            'type': 'structural',
            'users': users_data,
        }
        serializer = CreateOrganizationSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        org = serializer.save()
        self.assertEqual(org.new_users, users_data)
        self.assertEqual(org.name, 'New org name')


class RoleModelTest(TestCase):
    def test_role_records_created(self):
        """ Test MoveRoleRecords are created when Role.user changes. """
        user = User.objects.create()
        org = Organization.objects.create()

        role = Role.objects.create(name='CEO', organization=org, user=user)
        record_one = MoveRoleRecord.objects.filter().latest()
        self.assertEqual(record_one.user, user)
        self.assertEqual(record_one.to_role, role)
        self.assertEqual(record_one.from_role, None)

        role.user = None
        role.save()

        self.assertEqual(MoveRoleRecord.objects.all().count(), 2)
        record_two = MoveRoleRecord.objects.all().latest()
        self.assertEqual(record_two.user, user)
        self.assertEqual(record_two.to_role, None)
        self.assertEqual(record_two.from_role, role)


class RoleSerializerTest(TestCase):
    def test_role_attributes_transformed(self):
        """ Test role user and parent attributes are transformed. """
        ## Test without instance
        data = RoleSerializer(None).data
        self.assertIsNone(data['user'])
        self.assertIsNone(data['parent'])

        # Test with instance
        org = Organization.objects.create()
        user = User.objects.create()
        parent_role = Role.objects.create(organization=org)
        role = Role.objects.create(organization=org, parent=parent_role,
                                   user=user)

        data = RoleSerializer(role).data
        self.assertIn('id', data['user'].keys())
        self.assertIn('id', data['parent'].keys())


class RoleViewSetTest(TestCase):
    def test_pre_save(self):
        """ Test organization is set when creating object. """
        organization = Organization.objects.create()
        obj = Mock(organization_id=None)
        view = RoleViewSet()
        view.organization = organization
        view.pre_save(obj)
        self.assertEqual(obj.organization, organization)


class OrganizationModelTest(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create()

    def test_user_is_administrative(self):
        good_user = User.objects.create(email='good@example.com')
        bad_user = User.objects.create(email='bad@example.com')
        OrganizationMembership.objects.create(user=good_user,
                                              organization=self.organization,
                                              administrative_level='superuser')
        OrganizationMembership.objects.create(user=bad_user,
                                              organization=self.organization,
                                              administrative_level='user')
        self.assertTrue(self.organization.user_is_administrative(good_user))
        self.assertFalse(self.organization.user_is_administrative(bad_user))

    def test_visible_members(self):
        user = User.objects.create(email='visable@example.com')
        hidden_user = User.objects.create(email='hidden@example.com')
        OrganizationMembership.objects.create(user=user,
                                              organization=self.organization,
                                              administrative_level='user')
        OrganizationMembership.objects.create(user=hidden_user, hidden=True,
                                              organization=self.organization,
                                              administrative_level='user')
        members = self.organization.visible_members
        self.assertIn(user, members)
        self.assertNotIn(hidden_user, members)

    def test_get_statistics_month(self):
        """ Validate get_statistics() 'stats_by_month' output. """
        for i in range(0, 10):
            date = datetime(2012, 12, 30) - timedelta(days=i)
            OrganizationStatistic.objects.create(
                organization=self.organization, date=date, num_roles=100,
                num_roles_filled=101, num_roles_unfilled=102,
                num_external_roles=103, num_teams=104, num_workgroups=105,
                num_livedocs_active=106, num_livedocs_completed=107,
                num_documents=108, num_documents_static=109,
                average_time_questions_open=110, num_questions=111,
                num_answers=112)

        data = self.organization.get_statistics()
        stats = data['stats_by_month'][0]
        self.assertEqual(stats['num_documents'], 108.0)
        self.assertEqual(stats['num_roles_unfilled'], 102.0)
        self.assertEqual(stats['average_time_questions_open'], 110.0)
        self.assertEqual(stats['num_livedocs_active'], 106.0)
        self.assertEqual(stats['num_livedocs_completed'], 1070.0)
        self.assertEqual(stats['num_external_roles'], 103.0)
        self.assertEqual(stats['num_questions'], 1110.0)
        self.assertEqual(stats['num_workgroups'], 105.0)
        self.assertEqual(stats['num_documents_static'], 109.0)
        self.assertEqual(stats['num_roles_filled'], 101.0)
        self.assertEqual(stats['num_roles'], 100.0)
        self.assertEqual(stats['num_teams'], 104.0)
        self.assertEqual(stats['num_answers'], 1120.0)

    def test_get_statistics_roles(self):
        """ Validate get_statistics() 'role_succession' output. """
        root1 = self.organization.roles.create(name='Root 1')
        child1 = self.organization.roles.create(name='Root 1', parent=root1)
        root2 = self.organization.roles.create(name='Root 2')
        user = User.objects.create()
        for role in (root1, child1, root2):
            role.user = user
            role.save()

        data = self.organization.get_statistics()
        self.assertEqual(data['role_succession'], [[u'Root 1', 2],
                                                   [u'Root 2', 1]])


class IsOrganizationSuperOrAdminOrReadOnlyTest(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create()
        self.good_user = User.objects.create(email='good@example.com')
        self.bad_user = User.objects.create(email='bad@example.com')

    def test_superuser_permission(self):
        """ Test superusers have access. """
        bad_user2 = User.objects.create(email='bad2@example.com')
        OrganizationMembership.objects.create(user=self.good_user,
                                              organization=self.organization,
                                              administrative_level='superuser')
        OrganizationMembership.objects.create(user=bad_user2,
                                              organization=self.organization,
                                              administrative_level='user')

        permission = IsOrganizationSuperOrAdminOrReadOnly()
        view = Mock(organization=self.organization)

        request = Mock(user=self.bad_user, method='POST')
        self.assertFalse(permission.has_permission(request, view))

        request = Mock(user=bad_user2, method='POST')
        self.assertFalse(permission.has_permission(request, view))

        request = Mock(user=self.good_user, method='POST')
        self.assertTrue(permission.has_permission(request, view))

    def test_read_only_permission(self):
        """ Test anyone can read. """
        permission = IsOrganizationSuperOrAdminOrReadOnly()

        request = Mock(user=self.bad_user, method='GET')
        self.assertTrue(permission.has_permission(request, None))


class IsInOrganizationTest(TestCase):
    def test_creator_permission(self):
        """ Test superusers have access. """
        organization = Organization.objects.create()
        good_user = User.objects.create(email='good@example.com')
        bad_user = User.objects.create(email='bad@example.com')
        OrganizationMembership.objects.create(user=good_user,
                                              organization=organization,
                                              administrative_level='superuser')

        permission = IsInOrganization()
        view = Mock(organization=organization)

        request = Mock(user=bad_user, method='GET')
        self.assertFalse(permission.has_permission(request, view))

        request = Mock(user=good_user, method='GET')
        self.assertTrue(permission.has_permission(request, view))


class OrganizationMembershipSerializerTest(TestCase):
    def test_user_attribute_transformed(self):
        """ Test membership user attribute is transformed. """
        ## Test without instance
        data = UserOrganizationMembershipSerializer(None).data
        self.assertIsNone(data['user'])

        # Test with instance
        organization = Organization.objects.create()
        user = User.objects.create(email='user@example.com')
        membership = OrganizationMembership(user=user,
                                            organization=organization,
                                            administrative_level='superuser')
        membership.save()

        ctx = {'view': Mock(organization=organization)}
        data = UserOrganizationMembershipSerializer(membership,
                                                    context=ctx).data
        self.assertIn('id', data['user'].keys())

    def test_membership_attribute_transformed(self):
        """
        Test membership organization and roles attributes are transformed.
        """
        organization = Organization.objects.create()
        ctx = {'view': Mock(organization=organization)}

        # Test with instance
        user = User.objects.create(email='user@example.com')
        membership = OrganizationMembership(user=user,
                                            organization=organization,
                                            administrative_level='superuser')
        membership.save()
        Role(organization=organization, user=user).save()

        data = OrganizationMembershipSerializer(membership, context=ctx).data
        self.assertIn('id', data['organization'].keys())
        self.assertIn('id', data['roles'][0].keys())


class MembershipViewSetTest(TestCase):
    def test_get_serializer_class(self):
        """
        Test OrganizationMembershipSerializer is used for PUT requests.
        """
        organization = Organization.objects.create()
        view = MembershipViewSet(kwargs={'organization': organization.pk})

        view.request = Mock(method='PUT')
        self.assertEqual(view.get_serializer_class(),
                         OrganizationMembershipSerializer)

        view.request = Mock(method='GET')
        self.assertEqual(view.get_serializer_class(),
                         UserOrganizationMembershipSerializer)

    def test_get_queryset(self):
        """ Test only organization memberships are returned. """
        user1 = User.objects.create(email='user1@example.com')
        user2 = User.objects.create(email='user2@example.com')

        org1 = Organization.objects.create(name='Org 1', type='structural')
        OrganizationMembership.objects.create(user=user1, organization=org1)

        org2 = Organization.objects.create(name='Org 2', type='structural')
        OrganizationMembership.objects.create(user=user2, organization=org2)

        view = MembershipViewSet(organization=org1)
        members = [m.user for m in view.get_queryset()]
        self.assertIn(user1, members)
        self.assertNotIn(user2, members)

        view = MembershipViewSet()
        self.assertEqual(len(view.get_queryset()), 0)


class ModifyUserPermissionTest(TestCase):
    def test_has_permission(self):
        """ Test superusers have access. """
        organization = Organization.objects.create()
        good_user = User.objects.create(email='good@example.com')
        bad_user = User.objects.create(email='bad@example.com')
        OrganizationMembership.objects.create(user=good_user,
                                              organization=organization,
                                              administrative_level='superuser')
        OrganizationMembership.objects.create(user=bad_user,
                                              organization=organization,
                                              administrative_level='user')

        permission = ModifyUserPermission()
        view = Mock(organization=organization)

        request = Mock(user=bad_user, method='GET')
        self.assertFalse(permission.has_permission(request, view))

        request = Mock(user=good_user, method='GET')
        self.assertTrue(permission.has_permission(request, view))


class UserViewSetTest(TestCase):
    def test_get_serializer_class(self):
        """ Test correct serializer is used. """
        view = UserViewSet(kwargs={})
        view.request = Mock()

        view.request.method = 'POST'
        self.assertEqual(view.get_serializer_class(),
                         CreateUserSerializer)

        view.request.method = 'PUT'
        self.assertEqual(view.get_serializer_class(),
                         UpdateUserSerializer)

        user = User.objects.create()
        view.request.method = 'POST'
        view.kwargs['pk'] = user.pk
        self.assertEqual(view.get_serializer_class(instance=user),
                         UserSerializer)
