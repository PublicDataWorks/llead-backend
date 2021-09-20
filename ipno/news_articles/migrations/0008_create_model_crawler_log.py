# Generated by Django 3.1.4 on 2021-09-01 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_articles', '0007_allow_author_nullable'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrawlerLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('source_name', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('started', 'Started'), ('finished', 'Finished'), ('error', 'Error')], max_length=32)),
                ('created_rows', models.IntegerField(null=True)),
                ('error_rows', models.IntegerField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]