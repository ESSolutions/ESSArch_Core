# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-15 09:09
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixity', '0002_auto_20171122_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='validation',
            name='specification',
            field=models.JSONField(null=True),
        ),
    ]
