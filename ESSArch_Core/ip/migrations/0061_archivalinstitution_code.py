# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-11 09:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ip', '0059_auto_20171212_1124'),
    ]

    operations = [
        migrations.AddField(
            model_name='archivalinstitution',
            name='code',
            field=models.CharField(blank=True, max_length=16, null=True, unique=True),
        ),
    ]
