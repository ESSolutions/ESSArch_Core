# Generated by Django 2.2.5 on 2019-10-01 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('essauth', '0018_auto_20190430_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='language',
            field=models.CharField(default='', max_length=10),
        ),
    ]