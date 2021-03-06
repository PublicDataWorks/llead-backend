# Generated by Django 3.1.4 on 2021-04-22 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0006_department_officers'),
        ('officers', '0012_event'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='officer',
            name='employee_id',
        ),
        migrations.AddField(
            model_name='officer',
            name='departments',
            field=models.ManyToManyField(through='officers.Event', to='departments.Department'),
        ),
    ]
