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
            name='Attendance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('status', models.IntegerField(default=0)),
                ('cause_of_absence', models.CharField(max_length=200)),
                ('class_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classes.Classes')),
            ],
        ),
    ]
