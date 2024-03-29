# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-08-29 07:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0027_oracleinterfacereportreceipient'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentTotal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('settlement_date', models.DateField(blank=True, null=True)),
                ('bpoint_gateway_total', models.DecimalField(decimal_places=2, default='0.00', max_digits=8)),
                ('ledger_bpoint_total', models.DecimalField(decimal_places=2, default='0.00', max_digits=8)),
                ('oracle_parser_total', models.DecimalField(decimal_places=2, default='0.00', max_digits=8)),
                ('oracle_receipt_total', models.DecimalField(decimal_places=2, default='0.00', max_digits=8)),
                ('cash_total', models.DecimalField(decimal_places=2, default='0.00', max_digits=8)),
                ('bpay_total', models.DecimalField(decimal_places=2, default='0.00', max_digits=8)),
                ('oracle_system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payments.OracleInterfaceSystem')),
            ],
        ),
    ]
