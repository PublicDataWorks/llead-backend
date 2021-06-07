# Generated by Django 3.1.4 on 2021-05-10 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0008_generate_department_slug_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='slug',
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
    ]