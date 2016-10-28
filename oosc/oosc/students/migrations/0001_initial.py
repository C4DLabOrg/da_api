# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-28 16:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('classes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Students',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.IntegerField(default=0)),
                ('emis_code', models.IntegerField(default=0)),
                ('student_name', models.CharField(max_length=200)),
                ('date_of_birth', models.DateTimeField()),
                ('admission_no', models.IntegerField(default=0)),
                ('gender', models.IntegerField(default=0)),
                ('previous_class', models.IntegerField(default=0)),
                ('mode_of_transport', models.CharField(max_length=200)),
                ('time_to_school', models.IntegerField(default=0)),
                ('stay_with', models.CharField(max_length=200)),
                ('household', models.IntegerField(default=0)),
                ('meals_per_day', models.IntegerField(default=0)),
                ('not_in_school_before', models.IntegerField(default=0)),
                ('emis_code_histories', models.CharField(max_length=200)),
                ('class_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classes.Classes')),
            ],
        ),
    ]
