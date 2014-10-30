from mock import Mock, patch
from django_nose import FastFixtureTestCase as TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from apps.accounts.models import Organization

from .models import Document, DocumentVersion
from .views import HasAccessToDocument, DocumentViewSet
from .serializers import (CreateDocumentSerializer, UpdateDocumentSerializer,
                          DocumentSerializer, CondensedDocumentSerializer)

User = get_user_model()


class HasAccessToDocumentTest(TestCase):
    def test_has_access_permission(self):
        """ Test Document.user_has_access(user) is called. """
        permission = HasAccessToDocument()
        obj = Mock(user_has_access=Mock(return_value=False))
        request = Mock(user='request_user')
        self.assertFalse(permission.has_object_permission(request, None, obj))
        obj.user_has_access.assert_called_with_once('request_user')


class DocumentViewSetTest(TestCase):
    def test_get_queryset(self):
        """ Test only documents where user is a member are returned. """

        with patch('visualorg.apps.documents.views.Document') as MDoc:
            MDoc = Mock()
            view = DocumentViewSet()
            view.request = Mock(user='user', GET={})
            view.get_queryset()
            MDoc.objects.filter_for_user.assert_called_with_once('user')

    def test_get_serializer_class(self):
        """ Test correct serializers are used. """
        view = DocumentViewSet(kwargs={})

        view.request = Mock(method='POST')
        self.assertEqual(view.get_serializer_class(),
                         CreateDocumentSerializer)

        view.request = Mock(method='GET')
        self.assertEqual(view.get_serializer_class(),
                         CondensedDocumentSerializer)

        view.kwargs['pk'] = 1
        view.request = Mock(method='PUT')
        self.assertEqual(view.get_serializer_class(),
                         UpdateDocumentSerializer)

        view.kwargs['pk'] = 1
        view.request = Mock(method='GET')
        self.assertEqual(view.get_serializer_class(),
                         DocumentSerializer)

    def test_pre_save(self):
        """ Test created_by is set when creating object. """
        created_by = User.objects.create()
        obj = Mock(created_by_id=None)
        view = DocumentViewSet()
        view.request = Mock(user=created_by)
        view.pre_save(obj)
        self.assertEqual(obj.created_by, created_by)

    def test_post_save(self):
        """ Document version is created from new_file. """
        doc = Mock()
        doc.new_file = 'new_file'

        view = DocumentViewSet()
        view.post_save(doc, created=True)

        doc.documentversion_set.create.assert_called_with_once(file='new_file')

    def test_version_endpoint(self):
        """ DocumentViewSet.version(). """
        org = Organization.objects.create()
        doc = Document.objects.create(organization=org,
                                      visibility=Document.PUBLIC)
        user = User.objects.create()
        doc_file = SimpleUploadedFile("doc_file.txt", "The content")
        view = DocumentViewSet()
        view.request = Mock(method='POST', GET={}, DATA={}, user=user,
                            FILES={'file': doc_file})
        view.kwargs = {'pk': doc.pk}
        response = view.version(view.request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'Created document version.')


class DocumentVersionModelTest(TestCase):
    def test_version_are_incremented(self):
        """ Test DocumentVersion.version is incremented. """
        doc = Document(pk=1)

        doc_version = DocumentVersion.objects.create(document=doc)
        self.assertEqual(doc_version.version, 1)

        doc_version = DocumentVersion.objects.create(document=doc)
        self.assertEqual(doc_version.version, 2)


class CreateDocumentSerializerTest(TestCase):
    def test_file_is_attached(self):
        """ Test file is set on Document.new_file. """
        doc_file = SimpleUploadedFile("doc_file.txt", "The content")
        org = Organization.objects.create()
        data = {
            'title': 'Doc title',
            'organization': org.pk,
            'filetype': 'filetype',
            'visibility': 'public',
        }
        files = {
            'file': doc_file,
        }
        serializer = CreateDocumentSerializer(data=data, files=files)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        doc = serializer.save()
        self.assertEqual(doc.new_file, doc_file)

    def test_file_removed(self):
        """ Test file is removed from serializer.data. """
        serializer = CreateDocumentSerializer(Document())
        self.assertRaises(KeyError, lambda: serializer.data['file'])
