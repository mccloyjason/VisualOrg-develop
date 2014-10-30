from rest_framework import viewsets, mixins, permissions

from apps.utils.views import AdvancedAPIMixin

from .models import (
    Process, ProcessStep, ProcessStepTask, ProcessType, ProcessInstance,
    ProcessStepAssignment)
from .serializers import (
    CondensedProcessSerializer, ProcessSerializer, ProcessStepSerializer,
    CondensedProcessStepSerializer, ProcessStepTaskSerializer,
    ProcessTypeSerializer, ProcessInstanceSerializer,
    CondensedProcessInstanceSerializer, ProcessStepAssignmentSerializer)


class CanAccessProcess(permissions.BasePermission):
    """ Deny access to process if user does not have permission. """
    def has_object_permission(self, request, view, obj):
        return obj in Process.get_available_to_user(request.user)


class CanAccessProcessStep(permissions.BasePermission):
    """ Deny access to process if user does not have permission. """
    def has_permission(self, request, view):
        try:
            Process.get_available_to_user(request.user).get(
                pk=view.kwargs['process'])
        except Process.DoesNotExist:
            return False
        return True


class CanAccessProcessInstance(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj in ProcessInstance.get_available_to_user(request.user)


class CanAccessProcessInstanceAssignments(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            ProcessInstance.get_available_to_user(request.user).get(
                pk=view.kwargs['instance'])
        except Process.DoesNotExist:
            return False
        return True


class ProcessViewSet(AdvancedAPIMixin, mixins.ListModelMixin,
                     mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                     mixins.DestroyModelMixin, mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    model = Process
    permission_classes = (permissions.IsAuthenticated, CanAccessProcess)
    condensed_serializer = CondensedProcessSerializer
    full_serializer = ProcessSerializer

    def get_queryset(self):
        return Process.get_available_to_user(self.request.user)

    def pre_save(self, obj):
        if not obj.pk:
            obj.created_by = self.request.user

    def post_save(self, obj, created=False):
        if created:
            obj.shared_with.add(self.request.user)


class ProcessStepViewSet(AdvancedAPIMixin, mixins.ListModelMixin,
                         mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                         mixins.DestroyModelMixin, mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):
    model = ProcessStep
    full_serializer = ProcessStepSerializer
    condensed_serializer = CondensedProcessStepSerializer
    permission_classes = (permissions.IsAuthenticated, CanAccessProcessStep)

    def get_queryset(self):
        return ProcessStep.objects.filter(parent=self.kwargs['process'])

    def pre_save(self, obj):
        if not obj.parent_id:
            obj.parent = Process.objects.get(pk=self.kwargs['process'])


class ProcessStepTaskViewSet(AdvancedAPIMixin, mixins.ListModelMixin,
                             mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                             mixins.DestroyModelMixin, mixins.UpdateModelMixin,
                             viewsets.GenericViewSet):
    model = ProcessStepTask
    full_serializer = ProcessStepTaskSerializer
    condensed_serializer = ProcessStepTaskSerializer
    permission_classes = (permissions.IsAuthenticated, CanAccessProcessStep)

    def get_queryset(self):
        return ProcessStepTask.objects.filter(
            parent=self.kwargs['step'],
            parent__parent=self.kwargs['process'])

    def pre_save(self, obj):
        if not obj.parent_id:
            obj.parent_id = self.kwargs['step']


class ProcessTypeViewSet(AdvancedAPIMixin, mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    model = ProcessType
    full_serializer = ProcessTypeSerializer
    condensed_serializer = ProcessTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return ProcessType.objects.all()


class ProcessInstanceViewSet(AdvancedAPIMixin, mixins.ListModelMixin,
                             mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                             mixins.DestroyModelMixin, mixins.UpdateModelMixin,
                             viewsets.GenericViewSet):
    model = ProcessInstance
    full_serializer = ProcessInstanceSerializer
    condensed_serializer = CondensedProcessInstanceSerializer
    permission_classes = (permissions.IsAuthenticated,
                          CanAccessProcessInstance)

    def get_queryset(self):
        return ProcessInstance.get_available_to_user(self.request.user)

    def pre_save(self, obj):
        if not obj.pk:
            obj.initiated_by = self.request.user
            obj.organization = obj.process.organization

    def post_save(self, obj, created=False):
        if created:
            obj.shared_with.add(self.request.user)


class ProcessStepAssignmentViewSet(
        AdvancedAPIMixin, mixins.ListModelMixin,
        mixins.RetrieveModelMixin, mixins.CreateModelMixin,
        mixins.DestroyModelMixin, mixins.UpdateModelMixin,
        viewsets.GenericViewSet):
    model = ProcessStepAssignment
    full_serializer = ProcessStepAssignmentSerializer
    condensed_serializer = ProcessStepAssignmentSerializer
    permission_classes = (permissions.IsAuthenticated,
                          CanAccessProcessInstanceAssignments)

    def get_queryset(self):
        return ProcessStepAssignment.objects.filter(
            instance=self.kwargs['instance'])

    def pre_save(self, obj):
        if not obj.pk:
            obj.instance = ProcessInstance.objects.get(
                pk=self.kwargs['instance'])
