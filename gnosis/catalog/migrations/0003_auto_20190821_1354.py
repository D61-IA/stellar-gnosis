# Generated by Django 2.0.4 on 2019-08-21 03:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_note'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='note',
            name='author',
        ),
        migrations.DeleteModel(
            name='Note',
        ),
    ]
