# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-30 11:53
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0008_tag_information_package'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'permissions': (('search', 'Can search'), ('create_archive', 'Can create new archives'))},
        ),
    ]
