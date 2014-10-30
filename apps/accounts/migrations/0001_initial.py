# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'accounts_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=100, db_index=True)),
            ('external', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('activated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('reset_password_code', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
        ))
        db.send_create_signal(u'accounts', ['User'])

        # Adding model 'Role'
        db.create_table(u'accounts_role', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(related_name='roles', to=orm['accounts.Organization'])),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.Role'], null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='roles', to=orm['accounts.User'])),
        ))
        db.send_create_signal(u'accounts', ['Role'])

        # Adding M2M table for field related_to on 'Role'
        m2m_table_name = db.shorten_name(u'accounts_role_related_to')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_role', models.ForeignKey(orm[u'accounts.role'], null=False)),
            ('to_role', models.ForeignKey(orm[u'accounts.role'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_role_id', 'to_role_id'])

        # Adding model 'MoveRoleRecord'
        db.create_table(u'accounts_moverolerecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_role', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='from_move_role_records', null=True, to=orm['accounts.Role'])),
            ('to_role', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='to_move_role_records', null=True, to=orm['accounts.Role'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='move_role_records', to=orm['accounts.User'])),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'accounts', ['MoveRoleRecord'])

        # Adding model 'LoginRecord'
        db.create_table(u'accounts_loginrecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='login_records', to=orm['accounts.User'])),
        ))
        db.send_create_signal(u'accounts', ['LoginRecord'])

        # Adding model 'Organization'
        db.create_table(u'accounts_organization', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='organizations', null=True, to=orm['accounts.Organization'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('payment_plan', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='organizations', null=True, to=orm['billing.PaymentPlan'])),
            ('billing_contact', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='organizations', null=True, to=orm['accounts.User'])),
            ('trial_start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'accounts', ['Organization'])

        # Adding M2M table for field members on 'Organization'
        m2m_table_name = db.shorten_name(u'accounts_organization_members')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('organization', models.ForeignKey(orm[u'accounts.organization'], null=False)),
            ('user', models.ForeignKey(orm[u'accounts.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['organization_id', 'user_id'])

        # Adding model 'OrganizationMembership'
        db.create_table(u'accounts_organizationmembership', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='org_memberships', to=orm['accounts.User'])),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(related_name='org_memberships', to=orm['accounts.Organization'])),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('administrative_level', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'accounts', ['OrganizationMembership'])

        # Adding model 'OrganizationSettings'
        db.create_table(u'accounts_organizationsettings', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('organization', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['accounts.Organization'], unique=True)),
            ('document_visibility', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('org_hierarchy_visibility', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('livedoc_visibility', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('process_creation', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('process_editing', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('process_viewing', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('qa_configuration', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('default_org_view', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'accounts', ['OrganizationSettings'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'accounts_user')

        # Deleting model 'Role'
        db.delete_table(u'accounts_role')

        # Removing M2M table for field related_to on 'Role'
        db.delete_table(db.shorten_name(u'accounts_role_related_to'))

        # Deleting model 'MoveRoleRecord'
        db.delete_table(u'accounts_moverolerecord')

        # Deleting model 'LoginRecord'
        db.delete_table(u'accounts_loginrecord')

        # Deleting model 'Organization'
        db.delete_table(u'accounts_organization')

        # Removing M2M table for field members on 'Organization'
        db.delete_table(db.shorten_name(u'accounts_organization_members'))

        # Deleting model 'OrganizationMembership'
        db.delete_table(u'accounts_organizationmembership')

        # Deleting model 'OrganizationSettings'
        db.delete_table(u'accounts_organizationsettings')


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
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'organizations'", 'null': 'True', 'to': u"orm['accounts.Organization']"}),
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
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'to': u"orm['accounts.User']"})
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