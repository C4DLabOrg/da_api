# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-09 08:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0002_auto_20161116_2130'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teachers',
            old_name='school_id',
            new_name='school',
        ),
    ]
