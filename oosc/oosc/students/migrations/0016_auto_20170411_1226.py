# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-11 09:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0015_students_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='students',
            name='guardian_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='students',
            name='guardian_phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
