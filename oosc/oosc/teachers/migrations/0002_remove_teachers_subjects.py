# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-14 16:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teachers',
            name='subjects',
        ),
    ]
