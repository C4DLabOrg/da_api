# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-25 15:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Subjects',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject_id', models.IntegerField(default=0)),
                ('subject_name', models.CharField(max_length=200)),
            ],
        ),
    ]
