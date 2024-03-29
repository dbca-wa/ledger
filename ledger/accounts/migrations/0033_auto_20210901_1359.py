# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-09-01 05:59
from __future__ import unicode_literals

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0032_auto_20210604_1533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailuser',
            name='position_title',
            field=models.CharField(blank=True, help_text='Automatically synced from AD,  please contact service desk to update.', max_length=100, null=True, verbose_name='position title'),
        ),
        migrations.AlterField(
            model_name='privatedocument',
            name='upload',
            field=models.FileField(max_length=512, storage=django.core.files.storage.FileSystemStorage(base_url='/private-media/view/', location='/data/projects/ledger-master2/private-media'), upload_to='uploads/%Y/%m/%d'),
        ),
    ]
