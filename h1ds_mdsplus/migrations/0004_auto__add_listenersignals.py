# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ListenerSignals'
        db.create_table('h1ds_mdsplus_listenersignals', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('signal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds_core.H1DSSignal'])),
            ('listener', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['h1ds_mdsplus.MDSEventListener'])),
        ))
        db.send_create_signal('h1ds_mdsplus', ['ListenerSignals'])

        # Removing M2M table for field h1ds_signal on 'MDSEventListener'
        db.delete_table('h1ds_mdsplus_mdseventlistener_h1ds_signal')


    def backwards(self, orm):
        
        # Deleting model 'ListenerSignals'
        db.delete_table('h1ds_mdsplus_listenersignals')

        # Adding M2M table for field h1ds_signal on 'MDSEventListener'
        db.create_table('h1ds_mdsplus_mdseventlistener_h1ds_signal', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mdseventlistener', models.ForeignKey(orm['h1ds_mdsplus.mdseventlistener'], null=False)),
            ('h1dssignal', models.ForeignKey(orm['h1ds_core.h1dssignal'], null=False))
        ))
        db.create_unique('h1ds_mdsplus_mdseventlistener_h1ds_signal', ['mdseventlistener_id', 'h1dssignal_id'])


    models = {
        'h1ds_core.h1dssignal': {
            'Meta': {'object_name': 'H1DSSignal'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'h1ds_mdsplus.listenersignals': {
            'Meta': {'object_name': 'ListenerSignals'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listener': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['h1ds_mdsplus.MDSEventListener']"}),
            'signal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['h1ds_core.H1DSSignal']"})
        },
        'h1ds_mdsplus.mdseventinstance': {
            'Meta': {'ordering': "('-time',)", 'object_name': 'MDSEventInstance'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
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
            'Meta': {'ordering': "('name',)", 'object_name': 'MDSPlusTree'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['h1ds_mdsplus']
