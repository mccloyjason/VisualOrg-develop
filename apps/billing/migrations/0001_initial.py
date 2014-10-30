# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PaymentPlan'
        db.create_table(u'billing_paymentplan', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('max_users', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('monthly_cost', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'billing', ['PaymentPlan'])


    def backwards(self, orm):
        # Deleting model 'PaymentPlan'
        db.delete_table(u'billing_paymentplan')


    models = {
        u'billing.paymentplan': {
            'Meta': {'object_name': 'PaymentPlan'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_users': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'monthly_cost': ('django.db.models.fields.FloatField', [], {})
        }
    }

    complete_apps = ['billing']