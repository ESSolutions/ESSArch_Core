# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-28 14:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0014_tapedrive_locked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tapeslot',
            name='medium_id',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='The id for the medium, e.g. barcode'),
        ),
    ]
