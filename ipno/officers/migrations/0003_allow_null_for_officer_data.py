# Generated by Django 3.1.4 on 2021-02-25 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('officers', '0002_allow_blank_officer_history_dates'),
    ]

    operations = [
        migrations.AlterField(
            model_name='officer',
            name='birth_day',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='officer',
            name='birth_month',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='officer',
            name='birth_year',
            field=models.IntegerField(null=True),
        ),
    ]