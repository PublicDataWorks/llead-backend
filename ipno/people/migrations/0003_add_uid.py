# Generated by Django 3.1.13 on 2023-02-13 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0002_add_person_all_complaints_count_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='canonical_uid',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='uids',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
