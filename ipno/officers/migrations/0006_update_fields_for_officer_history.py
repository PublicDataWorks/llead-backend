# Generated by Django 3.1.4 on 2021-02-25 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('officers', '0005_add_more_fields_for_officer_history'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='officerhistory',
            name='agency',
        ),
        migrations.AlterField(
            model_name='officer',
            name='uid',
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
    ]
