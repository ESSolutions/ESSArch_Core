# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-08-09 13:58
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0011_auto_20180625_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='structure',
            name='specification',
            field=jsonfield.fields.JSONField(default={}),
        ),
    ]
