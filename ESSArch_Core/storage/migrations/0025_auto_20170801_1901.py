# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-01 17:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0024_auto_20170801_1658'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storageobject',
            name='last_changed_local',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
