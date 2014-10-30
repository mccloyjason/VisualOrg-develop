from rest_framework import serializers

from apps.accounts.serializers import CondensedUserSerializer

from .models import (
    Document, DocumentVersion, DocumentComment, LiveDocument,
    LiveDocumentSection)


class CreateDocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = ('file', )


class DocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = ('id', 'created_on', 'version', 'file')


class DocumentCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentComment
        fields = ('id', 'datetime', 'author', 'content', 'complete')


class CondensedDocumentSerializer(serializers.ModelSerializer):
    created_by = CondensedUserSerializer()

    class Meta:
        model = Document
        fields = ('id', 'title', 'filetype', 'created_by', 'created_on')


class DocumentSerializer(serializers.ModelSerializer):
    created_by = CondensedUserSerializer()
    current_version = DocumentVersionSerializer()
    comments = DocumentCommentSerializer(many=True)

    class Meta:
        model = Document
        fields = ('id', 'title', 'filetype', 'created_by', 'created_on',
                  'current_version', 'comments')


class CreateDocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField()

    class Meta:
        model = Document
        fields = ('id', 'title', 'filetype', 'visibility', 'organization',
                  'file')

    def restore_object(self, attrs, instance=None):
        file_obj = attrs.pop('file')
        obj = super(CreateDocumentSerializer, self).restore_object(attrs,
                                                                   instance)
        obj.new_file = file_obj
        return obj

    def to_native(self, *args, **kwargs):
        if args[0] is not None:
            self.fields.pop('file')
        return super(CreateDocumentSerializer, self).to_native(*args, **kwargs)


class UpdateDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('id', 'title', 'filetype', 'visibility')


class LiveDocumentSectionSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = LiveDocumentSection
        fields = ('id', 'title', 'reference_text_start', 'reference_text_end',
                  'instructional_text', 'content', 'order', 'assigned_to')

    def transform_assigned_to(self, obj, value):
        try:
            return CondensedUserSerializer(obj.assigned_to).data
        except AttributeError:
            return None


class CondensedLiveDocumentSerializer(serializers.ModelSerializer):
    created_by = CondensedUserSerializer(read_only=True)
    shared_with = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = LiveDocument
        fields = ('id', 'title', 'created_by', 'created_on', 'complete',
                  'organization', 'visibility', 'shared_with')

    def transform_shared_with(self, obj, value):
        try:
            return CondensedUserSerializer(obj.shared_with.all()).data
        except AttributeError:
            return None


class LiveDocumentSerializer(CondensedLiveDocumentSerializer):
    sections = LiveDocumentSectionSerializer(many=True, read_only=True)

    class Meta:
        model = LiveDocument
        fields = CondensedLiveDocumentSerializer.Meta.fields + (
            'sections', 'reference_text')
