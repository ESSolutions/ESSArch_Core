# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-25 09:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0012_structure_specification'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'permissions': (('search', 'Can search'), ('create_archive', 'Can create new archives'), ('delete_archive', 'Can delete archives'), ('change_tag_location', 'Can change tag location'))},
        ),
    ]
