# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-11 14:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0016_auto_20170411_1226'),
    ]

    operations = [
        migrations.AddField(
            model_name='students',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='students',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
