# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-17 18:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0029_auto_20180408_2119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storagemedium',
            name='tape_drive',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='storage_medium', to='storage.TapeDrive'),
        ),
        migrations.AlterField(
            model_name='storagemedium',
            name='tape_slot',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='storage_medium', to='storage.TapeSlot'),
        ),
    ]
