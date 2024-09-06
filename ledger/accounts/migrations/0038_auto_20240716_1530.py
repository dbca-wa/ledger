# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2024-07-16 07:30
from __future__ import unicode_literals

from django.conf import settings
import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0037_auto_20240714_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailuserchangelog',
            name='change_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='change_log_request_user', to=settings.AUTH_USER_MODEL),
        ),
    ]