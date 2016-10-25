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
            name='Teachers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teacher_id', models.IntegerField(default=0)),
                ('name', models.CharField(max_length=200)),
                ('phone_no', models.IntegerField(default=0)),
                ('type', models.IntegerField(default=0)),
                ('age', models.DateTimeField()),
                ('gender', models.CharField(max_length=200)),
                ('tsc_number', models.CharField(max_length=200)),
                ('bom_number', models.CharField(max_length=200)),
                ('qualifications', models.CharField(max_length=200)),
                ('subjects', models.CharField(max_length=200)),
                ('date_started_teaching', models.DateTimeField()),
                ('joined_current_school', models.DateTimeField()),
            ],
        ),
    ]
