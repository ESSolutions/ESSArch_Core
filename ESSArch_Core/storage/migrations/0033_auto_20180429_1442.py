# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-04-29 12:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0032_auto_20180426_1258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ioqueue',
            name='step',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='WorkflowEngine.ProcessStep'),
        ),
        migrations.AlterField(
            model_name='robotqueue',
            name='io_queue_entry',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='storage.IOQueue'),
        ),
    ]
