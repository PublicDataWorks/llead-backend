# Generated by Django 3.1.4 on 2021-05-20 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('complaints', '0006_alter_complaint_charges_to_textfield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaint',
            name='allegation_uid',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='charge_uid',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='complaint_uid',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
    ]