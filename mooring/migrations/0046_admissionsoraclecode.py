# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-08-23 04:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mooring', '0045_auto_20180823_1129'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdmissionsOracleCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oracle_code', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
    ]
