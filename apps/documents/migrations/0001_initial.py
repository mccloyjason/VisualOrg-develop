# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LiveDocument'
        db.create_table(u'documents_livedocument', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Organization'])),
            ('visibility', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('complete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('reference_text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'documents', ['LiveDocument'])

        # Adding model 'LiveDocumentSection'
        db.create_table(u'documents_livedocumentsection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('reference_text_start', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('reference_text_end', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('instructonal_text', self.gf('django.db.models.fields.TextField')()),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['documents.LiveDocument'])),
            ('assigned_to', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.User'], null=True)),
        ))
        db.send_create_signal(u'documents', ['LiveDocumentSection'])

        # Adding model 'LiveDocumentCompleteRecord'
        db.create_table(u'documents_livedocumentcompleterecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('live_document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['documents.LiveDocument'])),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'documents', ['LiveDocumentCompleteRecord'])

        # Adding model 'Document'
        db.create_table(u'documents_document', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('filetype', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.User'], null=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Organization'])),
            ('visibility', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'documents', ['Document'])

        # Adding model 'DocumentVersion'
        db.create_table(u'documents_documentversion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['documents.Document'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('version', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'documents', ['DocumentVersion'])

        # Adding model 'DocumentComment'
        db.create_table(u'documents_documentcomment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['documents.Document'])),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.User'], null=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('complete', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'documents', ['DocumentComment'])


    def backwards(self, orm):
        # Deleting model 'LiveDocument'
        db.delete_table(u'documents_livedocument')

        # Deleting model 'LiveDocumentSection'
        db.delete_table(u'documents_livedocumentsection')

        # Deleting model 'LiveDocumentCompleteRecord'
        db.delete_table(u'documents_livedocumentcompleterecord')

        # Deleting model 'Document'
        db.delete_table(u'documents_document')

        # Deleting model 'DocumentVersion'
        db.delete_table(u'documents_documentversion')

        # Deleting model 'DocumentComment'
        db.delete_table(u'documents_documentcomment')


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
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Organization']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'visibility': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'documents.documentcomment': {
            'Meta': {'object_name': 'DocumentComment'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.User']", 'null': 'True'}),
            'complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['documents.Document']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'documents.documentversion': {
            'Meta': {'object_name': 'DocumentVersion'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['documents.Document']"}),
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
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Organization']"}),
            'reference_text': ('django.db.models.fields.TextField', [], {}),
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
            'instructonal_text': ('django.db.models.fields.TextField', [], {}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['documents.LiveDocument']"}),
            'reference_text_end': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reference_text_start': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['documents']