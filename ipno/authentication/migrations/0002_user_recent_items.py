# Generated by Django 3.1.4 on 2021-07-19 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='recent_items',
            field=models.JSONField(blank=True, null=True),
        ),
    ]