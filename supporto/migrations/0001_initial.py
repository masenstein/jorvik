# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-09-04 17:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RestCache',
            fields=[
                ('request', models.TextField(primary_key=True, serialize=False)),
                ('response', models.TextField()),
                ('creazione', models.DateTimeField(auto_now=True, db_index=True)),
            ],
        ),
    ]
