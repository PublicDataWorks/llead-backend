# Generated by Django 3.1.4 on 2021-03-01 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0003_wrglfile'),
        ('documents', '0006_allow_blank_for_document_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='departments',
            field=models.ManyToManyField(blank=True, to='departments.Department'),
        ),
    ]
