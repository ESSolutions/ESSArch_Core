# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-18 13:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ip', '0040_auto_20170718_1453'),
    ]

    operations = [
        migrations.RenameField(
            model_name='eventip',
            old_name='eventApplication',
            new_name='task',
        ),
        migrations.AddField(
            model_name='eventip',
            name='application',
            field=models.CharField(default='ESSArch', max_length=255),
            preserve_default=False,
        ),
    ]
