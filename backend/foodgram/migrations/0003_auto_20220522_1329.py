# Generated by Django 3.2.13 on 2022-05-22 11:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='author',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='date_modified',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='last_editor',
        ),
    ]