# Generated by Django 3.1.4 on 2021-01-22 08:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0001_create_documents'),
        ('officers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='document_type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='officers',
            field=models.ManyToManyField(to='officers.Officer'),
        ),
        migrations.AddField(
            model_name='document',
            name='preview_image_url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
