# Generated by Django 3.1.13 on 2022-07-20 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_articles', '0022_rename_field_custom_matching_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsarticle',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
    ]
