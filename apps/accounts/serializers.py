import uuid

from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.alerts.serializers import AlertSerializer

from .models import Role, Organization, OrganizationMembership

User = get_user_model()


class CondensedOrganizationSerializer(serializers.ModelSerializer):
    primary_org = serializers.BooleanField(source='is_primary')
    object_counts = serializers.SerializerMethodField('get_object_counts')

    class Meta:
        model = Organization
        fields = ('id', 'name', 'type', 'primary_org')

    def get_object_counts(self, obj):
        return {
            'members': obj.members.count(),
            'suborgs': obj.children.count(),
            'roles': obj.roles.count(),
            'documents': obj.documents.count(),
            'live_documents': obj.live_documents.count()
        }


class CondensedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'external',
                  'activated')


class CondensedRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name')


class RoleSerializer(serializers.ModelSerializer):
    organization = CondensedOrganizationSerializer(source='organization',
                                                   read_only=True)
    user = serializers.PrimaryKeyRelatedField()
    parent = serializers.PrimaryKeyRelatedField(required=False)
    children = CondensedRoleSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ('id', 'name', 'organization', 'parent', 'children', 'user',
                  'related_to')

    def __init__(self, *args, **kwargs):
        super(RoleSerializer, self).__init__(*args, **kwargs)
        try:
            view = self.context['view']
        except KeyError:
            pass
        else:
            org = Organization.objects.get(pk=view.kwargs['organization'])
            # Limit users to organization members.
            self.fields['user'].queryset = org.members.all()
            # Limit parent to roles in organization.
            self.fields['parent'].queryset = org.roles.all()

    def transform_user(self, obj, value):
        try:
            return CondensedUserSerializer(obj.user).data
        except AttributeError:
            return None

    def transform_parent(self, obj, value):
        try:
            if obj.parent:
                return CondensedRoleSerializer(obj.parent).data
        except AttributeError:
            pass


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField('get_user_roles')

    class Meta:
        model = OrganizationMembership
        fields = ('id', 'organization', 'administrative_level', 'roles',
                  'hidden')
        read_only_fields = ('organization', )

    def get_user_roles(self, obj):
        return obj.organization.roles.filter(user=obj.user)

    def transform_organization(self, obj, value):
        return CondensedOrganizationSerializer(obj.organization).data

    def transform_roles(self, obj, value):
        roles = self.get_user_roles(obj)
        return CondensedRoleSerializer(roles, many=True).data


class UserOrganizationMembershipSerializer(OrganizationMembershipSerializer):
    user = serializers.PrimaryKeyRelatedField()

    class Meta(OrganizationMembershipSerializer.Meta):
        fields = ('id', 'organization', 'administrative_level', 'roles',
                  'hidden', 'user')

    def __init__(self, *args, **kwargs):
        super(UserOrganizationMembershipSerializer, self).__init__(*args,
                                                                   **kwargs)
        try:
            self.organization = self.context['view'].organization
        except KeyError:
            pass

    def transform_user(self, obj, value):
        try:
            return CondensedUserSerializer(obj.user).data
        except AttributeError:
            return None

    def validate_user(self, attrs, source):
        user = attrs[source]
        if self.organization.members.filter(pk=user.pk).count() >= 1:
            msg = 'User already member of organization.'
            raise serializers.ValidationError(msg)
        return attrs


class UserSerializer(serializers.ModelSerializer):
    memberships = OrganizationMembershipSerializer(required=False, many=True,
                                                   source='organization_memberships')

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'external',
                  'activated', 'memberships')


class AdvancedUserSerializer(serializers.ModelSerializer):
    memberships = OrganizationMembershipSerializer(required=False, many=True,
                                                   source='organization_memberships')
    alerts = AlertSerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'external',
                  'activated', 'memberships', 'alerts')


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'external',
                  'activated')


class UpdateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'external',
                  'activated', 'password')

    def __init__(self, *args, **kwargs):
        super(UpdateUserSerializer, self).__init__(*args, **kwargs)
        view = self.context['view']
        if args[0] != view.request.user:
            del self.fields['password']

    def restore_object(self, attrs, instance=None):
        password = attrs.pop('password', None)
        user = super(UpdateUserSerializer, self).restore_object(attrs,
                                                                instance)
        if password:
            user.set_password(password)
        return user

    def to_native(self, *args, **kwargs):
        if args[0] is not None:
            self.fields.pop('password', None)
        return super(UpdateUserSerializer, self).to_native(*args, **kwargs)


class UserInputSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    status = serializers.CharField()

    def validate_pk(self, attrs, source):
        pk = attrs[source]
        try:
            User.objects.get(pk=pk)
        except User.DoesNotExist:
            msg = 'User with pk {0} does not exist.'.format(pk)
            raise serializers.ValidationError(msg)
        return attrs


class OrganizationSerializer(serializers.ModelSerializer):
    parent = CondensedOrganizationSerializer()
    children = CondensedOrganizationSerializer(read_only=True, many=True)
    members = CondensedUserSerializer(source='visible_members')
    primary_org = serializers.BooleanField(read_only=True, source='is_primary')

    class Meta:
        model = Organization
        fields = ('id', 'name', 'type', 'primary_org', 'parent', 'children',
                  'members')


class CreateOrganizationSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField()
    users = UserInputSerializer(many=True)

    class Meta:
        model = Organization
        fields = ('name', 'type', 'parent', 'users')

    def restore_object(self, attrs, instance=None):
        users = attrs.pop('users')
        obj = super(CreateOrganizationSerializer, self).restore_object(attrs,
                                                                       instance)
        obj.new_users = users
        return obj


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer to create users.
    """
    organization_name = serializers.CharField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'organization_name', 'email',
                  'password')

    def restore_object(self, attrs, instance=None):
        if instance:
            raise Exception('RegisterSerializer is only for creating users.')

        organization_name = attrs.pop('organization_name')
        password = attrs.pop('password')

        user = super(RegisterSerializer, self).restore_object(attrs, instance)
        user.validation_code = uuid.uuid4().hex[:6]
        user.set_password(password)
        user.organization_name = organization_name
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ValidateCodeSerializer(serializers.Serializer):
    code = serializers.CharField()
    email = serializers.EmailField()


class PasswordForgotSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()
    password = serializers.CharField()
