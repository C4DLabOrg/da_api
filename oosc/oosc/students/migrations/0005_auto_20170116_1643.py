# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-16 13:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0004_students_absence'),
    ]

    operations = [
        migrations.RenameField(
            model_name='students',
            old_name='absence',
            new_name='total_absents',
        ),
    ]
