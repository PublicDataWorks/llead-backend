# Generated by Django 3.1.4 on 2021-09-24 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_articles', '0016_newsarticle_excluded_officers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsarticle',
            name='link',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]