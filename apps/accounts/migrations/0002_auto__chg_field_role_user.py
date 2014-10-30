# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Role.user'
        db.alter_column(u'accounts_role', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['accounts.User']))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Role.user'
        raise RuntimeError("Cannot reverse this migration. 'Role.user' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Role.user'
        db.alter_column(u'accounts_role', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.User']))

    models = {
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
            'billing_contact': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'organizations'", 'null': 'True', 'to': u"orm['accounts.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['accounts.User']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['accounts.Organization']"}),
            'payment_plan': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'organizations'", 'null': 'True', 'to': u"orm['billing.PaymentPlan']"}),
            'trial_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'accounts.organizationmembership': {
            'Meta': {'object_name': 'OrganizationMembership'},
            'administrative_level': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'org_memberships'", 'to': u"orm['accounts.Organization']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'org_memberships'", 'to': u"orm['accounts.User']"})
        },
        u'accounts.organizationsettings': {
            'Meta': {'object_name': 'OrganizationSettings'},
            'default_org_view': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'document_visibility': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'livedoc_visibility': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'org_hierarchy_visibility': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'organization': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['accounts.Organization']", 'unique': 'True'}),
            'process_creation': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'process_editing': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'process_viewing': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'qa_configuration': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'accounts.role': {
            'Meta': {'object_name': 'Role'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'to': u"orm['accounts.Organization']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Role']", 'null': 'True', 'blank': 'True'}),
            'related_to': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_to_rel_+'", 'to': u"orm['accounts.Role']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'null': 'True', 'to': u"orm['accounts.User']"})
        },
        u'accounts.user': {
            'Meta': {'object_name': 'User'},
            'activated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'external': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'reset_password_code': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        },
        u'billing.paymentplan': {
            'Meta': {'object_name': 'PaymentPlan'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_users': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'monthly_cost': ('django.db.models.fields.FloatField', [], {})
        }
    }

    complete_apps = ['accounts']