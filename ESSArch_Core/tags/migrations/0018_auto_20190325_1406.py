# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-25 13:06
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tags', '0017_search'),
    ]

    operations = [
        migrations.AddField(
            model_name='structure',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='created_structures', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='structure',
            name='revise_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='structure',
            name='revised_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='revised_structures', to=settings.AUTH_USER_MODEL),
        ),
    ]