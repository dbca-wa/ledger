# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2024-07-02 14:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0034_paymentinformationlink'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paymentinformationlink',
            old_name='textarea',
            new_name='description',
        ),
    ]
