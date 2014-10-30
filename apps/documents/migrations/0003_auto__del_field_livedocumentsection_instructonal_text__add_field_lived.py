# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'LiveDocumentSection.instructonal_text'
        db.delete_column(u'documents_livedocumentsection', 'instructonal_text')

        # Adding field 'LiveDocumentSection.instructional_text'
        db.add_column(u'documents_livedocumentsection', 'instructional_text',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'LiveDocument.primary_organization'
        db.add_column(u'documents_livedocument', 'primary_organization',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='all_live_documents', to=orm['accounts.Organization']),
                      keep_default=False)

        # Adding M2M table for field shared_with on 'LiveDocument'
        m2m_table_name = db.shorten_name(u'documents_livedocument_shared_with')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('livedocument', models.ForeignKey(orm[u'documents.livedocument'], null=False)),
            ('user', models.ForeignKey(orm[u'accounts.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['livedocument_id', 'user_id'])


    def backwards(self, orm):
        # Adding field 'LiveDocumentSection.instructonal_text'
        db.add_column(u'documents_livedocumentsection', 'instructonal_text',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Deleting field 'LiveDocumentSection.instructional_text'
        db.delete_column(u'documents_livedocumentsection', 'instructional_text')

        # Deleting field 'LiveDocument.primary_organization'
        db.delete_column(u'documents_livedocument', 'primary_organization_id')

        # Removing M2M table for field shared_with on 'LiveDocument'
        db.delete_table(db.shorten_name(u'documents_livedocument_shared_with'))


    models = {
        u'accounts.organization': {
            'Meta': {'object_name': 'Organization'},
            'billing_contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'organizations_billing'", 'null': 'True', 'to': u"orm['accounts.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'organizations'", 'symmetrical': 'False', 'through': u"orm['accounts.OrganizationMembership']", 'to': u"orm['accounts.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': u"orm['accounts.Organization']"}),
            'payment_plan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'organizations'", 'null': 'True', 'to': u"orm['billing.PaymentPlan']"}),
            'trial_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'accounts.organizationmembership': {
            'Meta': {'unique_together': "(('user', 'organization'),)", 'object_name': 'OrganizationMembership'},
            'administrative_level': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'memberships'", 'to': u"orm['accounts.Organization']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'organization_memberships'", 'to': u"orm['accounts.User']"})
        },
        u'accounts.user': {
            'Meta': {'object_name': 'User'},
            'activated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'external': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'reset_password_code': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'validation_code': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'billing.paymentplan': {
            'Meta': {'object_name': 'PaymentPlan'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_users': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'monthly_cost': ('django.db.models.fields.FloatField', [], {})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'documents.document': {
            'Meta': {'object_name': 'Document'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.User']", 'null': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'filetype': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'documents'", 'to': u"orm['accounts.Organization']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'visibility': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'documents.documentcomment': {
            'Meta': {'object_name': 'DocumentComment'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.User']", 'null': 'True'}),
            'complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'document': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': u"orm['documents.Document']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'documents.documentversion': {
            'Meta': {'ordering': "('-version',)", 'unique_together': "(('document', 'version'),)", 'object_name': 'DocumentVersion'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'document': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'versions'", 'to': u"orm['documents.Document']"}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'version': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'documents.livedocument': {
            'Meta': {'object_name': 'LiveDocument'},
            'complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'live_documents'", 'to': u"orm['accounts.Organization']"}),
            'primary_organization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'all_live_documents'", 'to': u"orm['accounts.Organization']"}),
            'reference_text': ('django.db.models.fields.TextField', [], {}),
            'shared_with': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'shared_live_documents'", 'symmetrical': 'False', 'to': u"orm['accounts.User']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'visibility': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'documents.livedocumentcompleterecord': {
            'Meta': {'object_name': 'LiveDocumentCompleteRecord'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'live_document': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['documents.LiveDocument']"})
        },
        u'documents.livedocumentsection': {
            'Meta': {'object_name': 'LiveDocumentSection'},
            'assigned_to': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.User']", 'null': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructional_text': ('django.db.models.fields.TextField', [], {}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sections'", 'to': u"orm['documents.LiveDocument']"}),
            'reference_text_end': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reference_text_start': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['documents']