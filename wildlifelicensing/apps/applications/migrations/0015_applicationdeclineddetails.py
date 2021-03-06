# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-01 09:22
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wl_applications', '0014_assessment_assigned_assessor'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationDeclinedDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField(blank=True)),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wl_applications.Application')),
                ('officer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
