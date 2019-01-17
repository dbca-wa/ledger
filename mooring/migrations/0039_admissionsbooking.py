# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-08-21 05:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mooring', '0038_merge_20180815_1534'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdmissionsBooking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arrivalDate', models.DateField()),
                ('overnightStay', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=255)),
                ('vesselRegNo', models.CharField(max_length=200)),
                ('noOfAdults', models.IntegerField()),
                ('noOfChidlren', models.IntegerField()),
                ('noOfInfants', models.IntegerField()),
                ('warningReferenceNo', models.CharField(max_length=200)),
            ],
        ),
    ]