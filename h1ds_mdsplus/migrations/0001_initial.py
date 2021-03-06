# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MDSPlusTree'
        db.create_table('h1ds_mdsplus_mdsplustree', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('h1ds_mdsplus', ['MDSPlusTree'])

        # Adding model 'MDSEventInstance'
        db.create_table('h1ds_mdsplus_mdseventinstance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('h1ds_mdsplus', ['MDSEventInstance'])


    def backwards(self, orm):
        
        # Deleting model 'MDSPlusTree'
        db.delete_table('h1ds_mdsplus_mdsplustree')

        # Deleting model 'MDSEventInstance'
        db.delete_table('h1ds_mdsplus_mdseventinstance')


    models = {
        'h1ds_mdsplus.mdseventinstance': {
            'Meta': {'ordering': "('-time',)", 'object_name': 'MDSEventInstance'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'h1ds_mdsplus.mdsplustree': {
            'Meta': {'ordering': "('name',)", 'object_name': 'MDSPlusTree'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['h1ds_mdsplus']
