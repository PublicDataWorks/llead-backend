# Generated by Django 3.1.13 on 2021-12-07 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('complaints', '0011_rename_complaint_uid_to_allegation_uid'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='traffic_stop',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]