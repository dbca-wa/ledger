# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-07-18 14:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0014_referral_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComplianceAmendmentReason',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=30, verbose_name='Reason')),
            ],
        ),
        migrations.CreateModel(
            name='ComplianceAmendmentStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=30, verbose_name='Status')),
            ],
        ),
        migrations.AlterField(
            model_name='complianceamendmentrequest',
            name='reason',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='disturbance.ComplianceAmendmentReason'),
        ),
        migrations.AlterField(
            model_name='complianceamendmentrequest',
            name='status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='disturbance.ComplianceAmendmentStatus'),
        ),
    ]
