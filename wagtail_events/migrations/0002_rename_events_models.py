# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-23 13:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wagtail_events', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='EventDetailPage',
            new_name='EventDetail',
        ),
        migrations.RenameModel(
            old_name='EventIndexPage',
            new_name='EventIndex',
        ),
        migrations.RenameModel(
            old_name='EventInstance',
            new_name='EventOccurrence',
        ),
    ]
