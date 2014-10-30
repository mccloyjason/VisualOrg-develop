from rest_framework import status, viewsets, permissions, mixins
from rest_framework.response import Response
from rest_framework.decorators import link
from rest_utils.mixins import CreateModelMixin
from rest_utils.permissions import DenyCreateOnPutPermission
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth import get_user_model, authenticate, login
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render_to_response,redirect
from django.http import HttpResponse

from apps.billing.models import PaymentPlan

from .models import Organization, OrganizationMembership, Role
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    ValidateCodeSerializer, PasswordResetSerializer, PasswordForgotSerializer,
    RoleSerializer, OrganizationSerializer, CreateOrganizationSerializer,
    CondensedOrganizationSerializer, OrganizationMembershipSerializer,
    UserOrganizationMembershipSerializer, CreateUserSerializer,
    UpdateUserSerializer)

User = get_user_model()


class RegisterViewSet(CreateModelMixin, viewsets.GenericViewSet):
    model = User

    def get_serializer_class(self, instance=None):
        if instance:
            return UserSerializer
        else:
            return RegisterSerializer

    def post_save(self, obj, created=False):
        if created:
            # Set up a new organization with a Free Trial payment plan
            payment_plan = PaymentPlan.objects.get_free_plan()
            org = Organization(name=obj.organization_name, type='structural',
                               payment_plan=payment_plan, trial_start=now(),
                               billing_contact=obj)
            org.save()

            # Add the user to the members list
            obj.add_to_organization(org, OrganizationMembership.SUPERUSER)

            # Email user
            subject = 'VisualOrg - Complete your registration'
            message = ('In order to complete the registration process, '
                       'please click the following link: '
                       '<a href="%(url)s">%(url)s</a> and enter the following '
                       'code: %(code)s') % {'url': reverse('validate-list'),
                                            'code': obj.validation_code,
                                            'email': obj.email}
            # TODO: Decide how frontend will handle this. We could send the
            # the user to example.com/#validate/{email}/{code}/ and have the
            # frontend send the code to the REST API. Otherwise the validate
            # view should be a standard view.

            send_mail(subject, message, settings.SERVER_EMAIL, [obj.email, ],
                      fail_silently=False)


class LoginViewSet(viewsets.ViewSet):
    """
    Login user
    """
    def create(self, request):
        serializer = LoginSerializer(data=request.DATA)
        if serializer.is_valid():
            email = serializer.data['email']
            password = serializer.data['password']
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=email, password=password)
        if not user:
            return Response({'errors': ['Login invalid.']},
                            status=status.HTTP_403_FORBIDDEN)
        if not user.is_active:
            return Response({'errors': ['Inactive user.']},
                            status=status.HTTP_403_FORBIDDEN)

        login(request, user)
        return Response(UserSerializer(user).data)


class ValidateUserViewSet(viewsets.ViewSet):
    """
    Validate code sent to user at registration. Activate account if valid.
    """
    def create(self, request):
        serializer = ValidateCodeSerializer(data=request.DATA)
        if serializer.is_valid():
            code = serializer.data['code']
            email = serializer.data['email']
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, validation_code=code)
        except User.DoesNotExist:
            return Response({'errors': ['Invalid code.']},
                            status=status.HTTP_403_FORBIDDEN)
        else:
            user.activated = True
            user.validation_code = None
            user.save()
            return Response({'status': 'Account verified.'})


class PasswordForgotViewSet(viewsets.ViewSet):
    """
    Generate a random token for the given email.
    """
    def create(self, request):
        serializer = PasswordForgotSerializer(data=request.DATA)
        if serializer.is_valid():
            email = serializer.data['email']
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Intentionally don't alert that the email does not exist.
            # This way we avoid scanning the database for real emails.
            pass
        else:
            user.initiate_reset_password_process()

        return Response({'status': 'Request processed.'})


class PasswordResetViewSet(viewsets.ViewSet):
    """
    Allow user to reset password.
    """
    def create(self, request):
        serializer = PasswordResetSerializer(data=request.DATA)
        if serializer.is_valid():
            email = serializer.data['email']
            code = serializer.data['code']
            password = serializer.data['password']
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, reset_password_code=code)
        except User.DoesNotExist:
            return Response({'errors': ['Invalid code.']},
                            status=status.HTTP_403_FORBIDDEN)

        else:
            user.set_password(password)
            user.reset_password_code = None
            user.save()
            return Response({'status': 'Password reset.'})


class OrganizationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                          CreateModelMixin, viewsets.GenericViewSet):
    model = Organization
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.organizations.all()

    def get_serializer_class(self, instance=None):
        if self.request.method == 'GET' and 'pk' not in self.kwargs:
            return CondensedOrganizationSerializer
        elif instance:
            return OrganizationSerializer
        else:
            return CreateOrganizationSerializer

    def post_save(self, obj, created=False):
        if created:
            for user in obj.new_users:
                user_obj = User.objects.get(pk=user['pk'])
                kwargs = {'user': user_obj, 'organization': obj}
                if user['status'] == 'hidden':
                    kwargs['hidden'] = True
                else:
                    kwargs['administrative_level'] = user['status']
                member = OrganizationMembership(**kwargs)
                member.save()

    @link()
    def statistics(self, request, pk=None):
        org = self.get_object()
        return Response(org.get_statistics())


class IsOrganizationSuperOrAdminOrReadOnly(permissions.BasePermission):
    """ Grant access for Superusers, Administrators, Supervisors. """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return view.organization.user_is_administrative(request.user)


class IsInOrganization(permissions.BasePermission):
    """ Only allow members of organization access. """
    def has_permission(self, request, view):
        try:
            user_pk = request.user.pk
            return view.organization.members.filter(pk=user_pk).count() >= 1
        except AttributeError:
            return False


class OrganizationRelatedMixin(object):
    def initial(self, *args, **kwargs):
        try:
            self.organization = Organization.objects.get(
                pk=self.kwargs['organization'])
        except KeyError:
            pass
        super(OrganizationRelatedMixin, self).initial(*args, **kwargs)

    def get_queryset(self):
        queryset = super(OrganizationRelatedMixin, self).get_queryset()
        try:
            return queryset.filter(organization=self.organization)
        except AttributeError:
            return queryset.none()

    def pre_save(self, obj):
        if not obj.organization_id:
            obj.organization = self.organization


class RoleViewSet(OrganizationRelatedMixin, mixins.CreateModelMixin,
                  mixins.UpdateModelMixin, viewsets.GenericViewSet):
    model = Role
    serializer_class = RoleSerializer
    permission_classes = (permissions.IsAuthenticated,
                          DenyCreateOnPutPermission,
                          IsOrganizationSuperOrAdminOrReadOnly)


class MembershipViewSet(OrganizationRelatedMixin, mixins.ListModelMixin,
                        mixins.CreateModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):

    model = OrganizationMembership
    permission_classes = (permissions.IsAuthenticated,
                          DenyCreateOnPutPermission, IsInOrganization,
                          IsOrganizationSuperOrAdminOrReadOnly)

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return OrganizationMembershipSerializer
        else:
            return UserOrganizationMembershipSerializer


class ModifyUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        """ Superusers, Administrators, Supervisors of primary group only. """
        kwargs = {
            'organization__parent__isnull': True,
            'administrative_level__in': (OrganizationMembership.SUPERUSER,
                                         OrganizationMembership.ADMINISTRATOR,
                                         OrganizationMembership.SUPERVISOR),
        }
        user = request.user
        return user.organization_memberships.filter(**kwargs).count() >= 1

    def has_object_permission(self, request, view, obj):
        """
        Users can modify themselves. Superusers, administrators, and
        supervisors can modify other users.
        """
        if obj == request.user:
            return True

        return obj.get_primary_org().user_is_administrative(request.user)


class UserViewSet(CreateModelMixin, mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin, viewsets.GenericViewSet):
    model = User
    permission_classes = (permissions.IsAuthenticated,
                          DenyCreateOnPutPermission, ModifyUserPermission)

    def get_serializer_class(self, instance=None):
        if self.request.method == 'PUT':
            return UpdateUserSerializer
        elif instance:
            return UserSerializer
        else:
            return CreateUserSerializer

    def pre_save(self, obj):
        self.was_activated = User.objects.get(pk=obj.pk).activated

    def post_save(self, obj, created=False):
        if created:
            # Add the user to the members list
            obj.add_to_organization(self.request.user.get_primary_org(),
                                    OrganizationMembership.USER)

            if obj.activated:
                obj.initiate_reset_password_process()
        else:
            if not self.was_activated and obj.activated:
                obj.initiate_reset_password_process()

    @link()
    def statistics(self, request, organization=None, pk=None):
        user = self.get_object()
        return Response(user.get_statistics(organization=organization))

class Login(TemplateView):
    template_name='login.html'

    def post(self, request, *args, **kwargs):
        email=request.POST.get('username')
        password=request.POST.get('password')
        print "ssssssssssssssssssss",email,password
        user=authenticate(username=email,password=password)
        print "userrrrrrrrrrrrrrrrr",user
        if user is not None:
            if user.is_active:
                login(request,user)
                return redirect('/home/')
            else:
                messages.success(request,'Account is not yet activated')
        else:
            messages.success(request,'Account with this Username and Password does not Exist')
        return render_to_response('login.html',context_instance=RequestContext(request))


class Home(TemplateView):
    template_name='dashboard/home.html'

@login_required
def logout(request):
    logout(request)
    return redirect('/dashboard/')


        
