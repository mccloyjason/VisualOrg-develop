from rest_framework import serializers

from apps.accounts.serializers import (CondensedUserSerializer,
                                                 CondensedOrganizationSerializer)

from .models import Question, Answer


class CondensedQuestionSerializer(serializers.ModelSerializer):
    created_by = CondensedUserSerializer()
    organization = CondensedOrganizationSerializer()

    class Meta:
        model = Question
        fields = ('id', 'created_by', 'created_datetime', 'organization',
                  'question', 'open')


class QuestionSerializer(serializers.ModelSerializer):
    # TODO: Remove organization field for updates
    created_by = CondensedUserSerializer(read_only=True)
    organization = serializers.PrimaryKeyRelatedField()
    shared_users = serializers.PrimaryKeyRelatedField(many=True,
                                                      required=False)
    shared_organizations = serializers.PrimaryKeyRelatedField(many=True,
                                                              required=False)

    class Meta:
        model = Question
        fields = ('id', 'created_by', 'created_datetime', 'organization',
                  'question', 'open', 'shared_users', 'shared_organizations')

    def __init__(self, *args, **kwargs):
        super(QuestionSerializer, self).__init__(*args, **kwargs)
        if args[0] is not None:
            self.fields['organization'].read_only = True

    def transform_organization(self, obj, value):
        try:
            return CondensedOrganizationSerializer(obj.organization).data
        except AttributeError:
            return None

    def transform_shared_users(self, obj, value):
        try:
            users = obj.shared_users.all()
            return CondensedUserSerializer(users, many=True).data
        except AttributeError:
            return None

    def transform_shared_organizations(self, obj, value):
        try:
            orgs = obj.shared_organizations.all()
            return CondensedOrganizationSerializer(orgs, many=True).data
        except AttributeError:
            return None


class AnswerSerializer(serializers.ModelSerializer):
    created_by = CondensedUserSerializer(read_only=True)

    class Meta:
        model = Answer
        fields = ('id', 'created_by', 'created_datetime', 'content')
