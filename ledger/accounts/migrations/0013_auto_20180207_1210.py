# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-02-07 04:10
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_auto_20180118_1505'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('abn', models.CharField(blank=True, max_length=50, null=True, verbose_name='ABN')),
                ('identification', models.FileField(blank=True, null=True, upload_to='uploads/%Y/%m/%d')),
            ],
        ),
        migrations.CreateModel(
            name='OrganisationAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line1', models.CharField(max_length=255, verbose_name='Line 1')),
                ('line2', models.CharField(blank=True, max_length=255, verbose_name='Line 2')),
                ('line3', models.CharField(blank=True, max_length=255, verbose_name='Line 3')),
                ('locality', models.CharField(max_length=255, verbose_name='Suburb / Town')),
                ('state', models.CharField(blank=True, default='WA', max_length=255)),
                ('country', django_countries.fields.CountryField(default='AU', max_length=2)),
                ('postcode', models.CharField(max_length=10)),
                ('search_text', models.TextField(editable=False)),
                ('hash', models.CharField(db_index=True, editable=False, max_length=255)),
                ('organisation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='adresses', to='accounts.Organisation')),
            ],
            options={
                'verbose_name_plural': 'organisation addresses',
            },
        ),
        migrations.AlterField(
            model_name='address',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_adresses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='organisation',
            name='billing_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='org_billing_address', to='accounts.OrganisationAddress'),
        ),
        migrations.AddField(
            model_name='organisation',
            name='postal_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='org_postal_address', to='accounts.OrganisationAddress'),
        ),
        migrations.AlterUniqueTogether(
            name='organisationaddress',
            unique_together=set([('organisation', 'hash')]),
        ),
    ]
