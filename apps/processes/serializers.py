from rest_framework import serializers

from apps.accounts.serializers import (
    CondensedUserSerializer, CondensedOrganizationSerializer,
    CondensedRoleSerializer)

from .models import (
    Process, ProcessStep, ProcessStepTask, ProcessType, ProcessInstance,
    ProcessStepAssignment)


class ProcessStepTaskSerializer(serializers.ModelSerializer):
    # TODO: Change to CondensedDocumentSerializer when implemented.
    document = serializers.PrimaryKeyRelatedField(required=False)

    class Meta:
        model = ProcessStepTask
        fields = ('id', 'criticality', 'order', 'frequency', 'description',
                  'document')


class ProcessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessType
        fields = ('id', 'name', 'shape')


class CondensedProcessStepSerializer(serializers.ModelSerializer):
    process_type = serializers.PrimaryKeyRelatedField()
    role = serializers.PrimaryKeyRelatedField()
    next_nodes = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = ProcessStep
        fields = ('id', 'title', 'root', 'description', 'process_type',
                  'role', 'next_nodes')

    def transform_process_type(self, obj, value):
        try:
            return ProcessTypeSerializer(obj.process_type).data
        except AttributeError:
            None

    def transform_role(self, obj, value):
        try:
            return CondensedRoleSerializer(obj.role).data
        except AttributeError:
            None


class ProcessStepSerializer(CondensedProcessStepSerializer):
    tasks = ProcessStepTaskSerializer(many=True, read_only=True)

    class Meta:
        model = ProcessStep
        fields = CondensedProcessStepSerializer.Meta.fields + ('tasks', )


class ProcessStepAssignmentSerializer(serializers.ModelSerializer):
    assigned_user = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = ProcessStepAssignment
        fields = ('id', 'step', 'assigned_user', 'amount_completed',
                  'completed')

    def transform_assigned_user(self, obj, value):
        try:
            return CondensedUserSerializer(obj.assigned_user).data
        except AttributeError:
            return None


class CondensedProcessSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField()
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    shared_with = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = Process
        fields = ('id', 'title', 'organization', 'visibility', 'created_by',
                  'shared_with')

    def transform_organization(self, obj, value):
        try:
            return CondensedOrganizationSerializer(obj.organization).data
        except AttributeError:
            return None

    def transform_created_by(self, obj, value):
        try:
            return CondensedUserSerializer(obj.created_by).data
        except AttributeError:
            return None

    def transform_shared_with(self, obj, value):
        try:
            return CondensedUserSerializer(obj.shared_with.all()).data
        except AttributeError:
            return None


class ProcessSerializer(CondensedProcessSerializer):
    steps = CondensedProcessStepSerializer(many=True, read_only=True)

    class Meta:
        model = Process
        fields = CondensedProcessSerializer.Meta.fields + ('steps', )


class CondensedProcessInstanceSerializer(serializers.ModelSerializer):
    process = serializers.PrimaryKeyRelatedField()
    initiated_by = CondensedUserSerializer(read_only=True)
    shared_with = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = ProcessInstance
        fields = ('id', 'process', 'initiated_by', 'start_datetime',
                  'completed', 'completed_on', 'shared_with', 'visibility')
        read_only_fields = ('completed_on', )

    def transform_process(self, obj, value):
        try:
            return CondensedProcessSerializer(obj.process).data
        except AttributeError:
            return None

    def transform_shared_with(self, obj, value):
        try:
            return CondensedUserSerializer(obj.shared_with.all()).data
        except AttributeError:
            return None


class ProcessInstanceSerializer(CondensedProcessInstanceSerializer):
    assignments = ProcessStepAssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = ProcessInstance
        fields = CondensedProcessInstanceSerializer.Meta.fields + (
            'assignments', )
        read_only_fields = CondensedProcessInstanceSerializer.Meta.read_only_fields
