# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-21 08:57
from __future__ import unicode_literals

from django.db import migrations, models


def idToObjid(apps, schema_editor):
    EventIP = apps.get_model("ip", "EventIP")
    InformationPackage = apps.get_model("ip", "InformationPackage")
    db_alias = schema_editor.connection.alias

    for e in EventIP.objects.using(db_alias).iterator():
        try:
            e.linkingObjectIdentifierValue = InformationPackage.objects.using(db_alias).get(pk=e.linkingObjectIdentifierValue).object_identifier_value
        except:
            e.linkingObjectIdentifierValue = ''

        e.save(update_fields=['linkingObjectIdentifierValue'])

def noneToEmpty(apps, schema_editor):
    EventIP = apps.get_model("ip", "EventIP")
    db_alias = schema_editor.connection.alias

    EventIP.objects.using(db_alias).filter(linkingObjectIdentifierValue__isnull=True).update(linkingObjectIdentifierValue='')
        
def nothing(apps, schema_editor):
    return


class Migration(migrations.Migration):

    dependencies = [
        ('ip', '0047_auto_20170920_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventip',
            name='linkingObjectIdentifierValue',
            field=models.ForeignKey('ip.InformationPackage', on_delete=models.SET_NULL, related_name='events', null=True, db_constraint=False),
        ),
        migrations.AlterField(
            model_name='eventip',
            name='linkingObjectIdentifierValue',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.RunPython(noneToEmpty, nothing),
        migrations.AlterField(
            model_name='eventip',
            name='linkingObjectIdentifierValue',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.RunPython(idToObjid, nothing),
    ]
