# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-02-26 19:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0008_auto_20180131_2259'),
    ]

    operations = [
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('year', models.IntegerField(default=2018)),
                ('term', models.CharField(choices=[(b'1', b'1st Term'), (b'2', b'2nd Term'), (b'3', b'3rd Term')], max_length=2)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
        ),
    ]
