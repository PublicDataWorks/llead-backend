# Generated by Django 3.1.4 on 2021-05-20 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('use_of_forces', '0001_create_use_of_force'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useofforce',
            name='uof_uid',
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
    ]
