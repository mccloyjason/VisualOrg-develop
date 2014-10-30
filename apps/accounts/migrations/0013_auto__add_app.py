# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'App'
        db.create_table(u'accounts_app', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'accounts', ['App'])


    def backwards(self, orm):
        # Deleting model 'App'
        db.delete_table(u'accounts_app')


    models = {
        u'accounts.app': {
            'Meta': {'object_name': 'App'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'accounts.loginrecord': {
            'Meta': {'object_name': 'LoginRecord'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'login_records'", 'to': u"orm['accounts.User']"})
        },
        u'accounts.moverolerecord': {
            'Meta': {'object_name': 'MoveRoleRecord'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_role': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'from_move_role_records'", 'null': 'True', 'to': u"orm['accounts.Role']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_role': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'to_move_role_records'", 'null': 'True', 'to': u"orm['accounts.Role']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'move_role_records'", 'to': u"orm['accounts.User']"})
        },
        u'accounts.organization': {
            'Meta': {'object_name': 'Organization'},
            'billing_contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'organizations_billing'", 'null': 'True', 'to': u"orm['accounts.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'organizations'", 'symmetrical': 'False', 'through': u"orm['accounts.OrganizationMembership']", 'to': u"orm['accounts.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': u"orm['accounts.Organization']"}),
            'payment_plan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'organizations'", 'null': 'True', 'to': u"orm['billing.PaymentPlan']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
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
        u'accounts.organizationsettings': {
            'Meta': {'object_name': 'OrganizationSettings'},
            'default_org_view': ('django.db.models.fields.CharField', [], {'default': "'visual'", 'max_length': '30'}),
            'document_visibility': ('django.db.models.fields.CharField', [], {'default': "'all'", 'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'livedoc_visibility': ('django.db.models.fields.CharField', [], {'default': "'all'", 'max_length': '30'}),
            'org_hierarchy_visibility': ('django.db.models.fields.PositiveIntegerField', [], {'default': '2'}),
            'organization': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['accounts.Organization']", 'unique': 'True'}),
            'process_creation': ('django.db.models.fields.CharField', [], {'default': "'all'", 'max_length': '30'}),
            'process_editing': ('django.db.models.fields.CharField', [], {'default': "'all'", 'max_length': '30'}),
            'process_viewing': ('django.db.models.fields.CharField', [], {'default': "'all'", 'max_length': '30'}),
            'qa_configuration': ('django.db.models.fields.CharField', [], {'default': "'open'", 'max_length': '30'})
        },
        u'accounts.organizationstatistic': {
            'Meta': {'unique_together': "(('date', 'organization'),)", 'object_name': 'OrganizationStatistic'},
            'average_time_questions_open': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_answers': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'num_documents': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'num_documents_static': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'num_external_roles': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'num_livedocs_active': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'num_livedocs_completed': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'num_questions': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'num_roles': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'num_roles_filled': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'num_roles_unfilled': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'num_teams': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'num_workgroups': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Organization']"})
        },
        u'accounts.role': {
            'Meta': {'object_name': 'Role'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'to': u"orm['accounts.Organization']"}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['accounts.Role']"}),
            'related_to': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_to_rel_+'", 'to': u"orm['accounts.Role']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
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
        u'accounts.userstatistic': {
            'Meta': {'unique_together': "(('date', 'user'),)", 'object_name': 'UserStatistic'},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_processes_developed': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'num_processes_initiated': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Organization']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.User']"})
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
        }
    }

    complete_apps = ['accounts']