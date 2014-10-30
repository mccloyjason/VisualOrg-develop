from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_utils.permissions import DenyCreateOnPutPermission

from apps.utils.views import AdvancedAPIMixin

from .models import Document, LiveDocument, LiveDocumentSection
from .serializers import (CondensedDocumentSerializer, DocumentSerializer,
                          CreateDocumentSerializer, UpdateDocumentSerializer,
                          CreateDocumentVersionSerializer,
                          CondensedLiveDocumentSerializer,
                          LiveDocumentSerializer,
                          LiveDocumentSectionSerializer)


class HasAccessToDocument(permissions.BasePermission):
    """ Grant access to users. """
    def has_object_permission(self, request, view, obj):
        return obj.user_has_access(request.user)


class CanAccessLiveDocument(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            LiveDocument.get_available_to_user(request.user).get(
                pk=view.kwargs['live_document'])
        except LiveDocument.DoesNotExist:
            return False
        return True


class DocumentViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin, mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin, viewsets.GenericViewSet):
    model = Document
    permission_classes = (permissions.IsAuthenticated,
                          DenyCreateOnPutPermission, HasAccessToDocument)

    def get_queryset(self):
        queryset = Document.objects.filter_for_user(self.request.user)

        organization = self.request.GET.get('organization', None)
        if organization:
            queryset = queryset.filter(organization=organization)

        return queryset

    def get_serializer_class(self, instance=None):
        if self.request.method == 'POST':
            return CreateDocumentSerializer
        elif 'pk' in self.kwargs:
            if self.request.method == 'PUT':
                return UpdateDocumentSerializer
            else:
                return DocumentSerializer
        else:
            return CondensedDocumentSerializer

    def pre_save(self, obj):
        if not obj.created_by_id:
            obj.created_by = self.request.user

    def post_save(self, obj, created=False):
        if created:
            obj.documentversion_set.create(file=obj.new_file)

    @action()
    def version(self, request, pk=None):
        serializer = CreateDocumentVersionSerializer(data=request.DATA,
                                                     files=request.FILES)
        if serializer.is_valid():
            serializer.object.document = self.get_object()
            serializer.save()
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': 'Created document version.'})


class LiveDocumentViewSet(AdvancedAPIMixin, mixins.ListModelMixin,
                          mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                          mixins.DestroyModelMixin, mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    model = LiveDocument
    permission_classes = (permissions.IsAuthenticated, )
    condensed_serializer = CondensedLiveDocumentSerializer
    full_serializer = LiveDocumentSerializer

    def get_queryset(self):
        return LiveDocument.get_available_to_user(self.request.user)

    def pre_save(self, obj):
        if not obj.pk:
            obj.created_by = self.request.user

    def post_save(self, obj, created=False):
        if created:
            obj.shared_with.add(self.request.user)


class LiveDocumentSectionViewSet(AdvancedAPIMixin, mixins.ListModelMixin,
                                 mixins.RetrieveModelMixin,
                                 mixins.CreateModelMixin,
                                 mixins.DestroyModelMixin,
                                 mixins.UpdateModelMixin,
                                 viewsets.GenericViewSet):
    model = LiveDocumentSection
    permission_classes = (permissions.IsAuthenticated, CanAccessLiveDocument)
    condensed_serializer = LiveDocumentSectionSerializer
    full_serializer = LiveDocumentSectionSerializer

    def get_queryset(self):
        return LiveDocumentSection.objects.filter(
            parent=self.kwargs['live_document'])

    def pre_save(self, obj):
        if not obj.pk:
            obj.parent = LiveDocument.objects.get(
                pk=self.kwargs['live_document'])
