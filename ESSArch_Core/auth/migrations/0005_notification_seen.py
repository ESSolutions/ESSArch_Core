# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-18 09:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('essauth', '0004_auto_20170915_1030'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='seen',
            field=models.BooleanField(default=False),
        ),
    ]
