# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Process.created_datetime'
        db.add_column(u'processes_process', 'created_datetime',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2014, 2, 4, 0, 0), blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Process.created_datetime'
        db.delete_column(u'processes_process', 'created_datetime')


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
        u'accounts.role': {
            'Meta': {'object_name': 'Role'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'to': u"orm['accounts.Organization']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['accounts.Role']"}),
            'related_to': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_to_rel_+'", 'to': u"orm['accounts.Role']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'null': 'True', 'to': u"orm['accounts.User']"})
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
        u'processes.process': {
            'Meta': {'object_name': 'Process'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_processes'", 'null': 'True', 'to': u"orm['accounts.User']"}),
            'created_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'processes'", 'to': u"orm['accounts.Organization']"}),
            'primary_organization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'all_processes'", 'to': u"orm['accounts.Organization']"}),
            'shared_with': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'shared_processes'", 'symmetrical': 'False', 'to': u"orm['accounts.User']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'visibility': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'processes.processinstance': {
            'Meta': {'object_name': 'ProcessInstance'},
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'completed_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initiated_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.User']"}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'process_instances'", 'to': u"orm['accounts.Organization']"}),
            'primary_organization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'all_process_instances'", 'to': u"orm['accounts.Organization']"}),
            'process': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'instances'", 'to': u"orm['processes.Process']"}),
            'shared_with': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'shared_process_instances'", 'symmetrical': 'False', 'to': u"orm['accounts.User']"}),
            'start_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'visibility': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'processes.processstep': {
            'Meta': {'object_name': 'ProcessStep'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'next_nodes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'+'", 'symmetrical': 'False', 'to': u"orm['processes.ProcessStep']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'steps'", 'to': u"orm['processes.Process']"}),
            'process_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['processes.ProcessType']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'processes'", 'to': u"orm['accounts.Role']"}),
            'root': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'processes.processstepassignment': {
            'Meta': {'object_name': 'ProcessStepAssignment'},
            'amount_completed': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'assigned_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignments'", 'to': u"orm['accounts.User']"}),
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignments'", 'to': u"orm['processes.ProcessInstance']"}),
            'step': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'assignment'", 'unique': 'True', 'to': u"orm['processes.ProcessStep']"})
        },
        u'processes.processsteptask': {
            'Meta': {'object_name': 'ProcessStepTask'},
            'criticality': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['documents.Document']", 'null': 'True', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks'", 'to': u"orm['processes.ProcessStep']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'processes.processtype': {
            'Meta': {'object_name': 'ProcessType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'shape': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['processes']