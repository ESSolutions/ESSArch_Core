# Generated by Django 2.0.13 on 2019-03-28 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0026_tagversion_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='structure',
            name='template',
            field=models.BooleanField(default=False, verbose_name='template'),
            preserve_default=False,
        ),
    ]