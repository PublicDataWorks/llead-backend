# Generated by Django 3.1.13 on 2021-12-29 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0015_add_agency_field'),
        ('departments', '0014_add_department_starred_news_articles'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='starred_documents',
            field=models.ManyToManyField(blank=True, related_name='starred_departments', to='documents.Document'),
        ),
    ]
