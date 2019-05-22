# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-04-10 08:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields
import mptt.fields
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('essauth', '0016_auto_20181221_1716'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='external_id',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='external id'),
        ),
        migrations.AddField(
            model_name='groupmemberrole',
            name='external_id',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='external id'),
        ),
    ]