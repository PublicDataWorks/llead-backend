# Generated by Django 3.1.4 on 2021-05-05 09:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('officers', '0014_add_more_kinds_to_event'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='use_of_force_uid',
        ),
    ]