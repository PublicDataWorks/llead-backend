# Generated by Django 3.1.13 on 2022-06-07 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('officers', '0026_add_appeal_relation_to_events'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='kind',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
    ]
