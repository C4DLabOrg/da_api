# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-22 13:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0010_auto_20170122_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='students',
            name='date_enrolled',
            field=models.DateTimeField(auto_created=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
