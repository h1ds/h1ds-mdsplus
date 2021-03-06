# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'MDSEventInstance'
        db.delete_table('h1ds_mdsplus_mdseventinstance')

        # Adding field 'MDSPlusTree.display_order'
        db.add_column('h1ds_mdsplus_mdsplustree', 'display_order', self.gf('django.db.models.fields.IntegerField')(default=10), keep_default=False)


    def backwards(self, orm):
        
        # Adding model 'MDSEventInstance'
        db.create_table('h1ds_mdsplus_mdseventinstance', (
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('h1ds_mdsplus', ['MDSEventInstance'])

        # Deleting field 'MDSPlusTree.display_order'
        db.delete_column('h1ds_mdsplus_mdsplustree', 'display_order')


    models = {
        'h1ds_core.h1dssignal': {
            'Meta': {'object_name': 'H1DSSignal'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'h1ds_mdsplus.listenersignals': {
            'Meta': {'object_name': 'ListenerSignals'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listener': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['h1ds_mdsplus.MDSEventListener']"}),
            'signal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['h1ds_core.H1DSSignal']"})
        },
        'h1ds_mdsplus.mdseventlistener': {
            'Meta': {'object_name': 'MDSEventListener'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'event_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'h1ds_signal': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['h1ds_core.H1DSSignal']", 'through': "orm['h1ds_mdsplus.ListenerSignals']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'server': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'h1ds_mdsplus.mdsplustree': {
            'Meta': {'ordering': "('display_order',)", 'object_name': 'MDSPlusTree'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'display_order': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['h1ds_mdsplus']
