# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-13 16:21
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('izmir', '0005_route_departure_times'),
    ]

    operations = [
        migrations.AlterField(
            model_name='route',
            name='departure_times',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.TimeField(), default=[], null=True, size=None), default=[], size=6, verbose_name='Departure Times'),
        ),
    ]