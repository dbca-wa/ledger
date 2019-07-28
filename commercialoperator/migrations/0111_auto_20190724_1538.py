# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-07-24 07:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commercialoperator', '0110_merge_20190722_0952'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationtype',
            name='is_gst_exempt',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='park',
            name='is_gst_exempt',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='proposaltype',
            name='name',
            field=models.CharField(choices=[('T Class', 'T Class')], default='T Class', max_length=64, verbose_name='Application name (eg. T Class, Filming, Event, E Class)'),
        ),
    ]