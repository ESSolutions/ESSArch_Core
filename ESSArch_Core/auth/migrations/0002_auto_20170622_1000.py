# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-22 08:00
from __future__ import unicode_literals

from django.db import migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('essauth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='ip_list_columns',
            field=picklefield.fields.PickledObjectField(default=[b'label', b'object_identifier_value', b'responsible', b'create_date', b'state', b'step_state', b'events', b'status', b'delete'], editable=False),
        ),
    ]
