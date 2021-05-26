# Generated by Django 3.1.4 on 2021-05-20 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('officers', '0018_add_unique_constraint_to_event_uid'),
        ('departments', '0006_department_officers'),
        ('complaints', '0007_add_db_index_for_complaints'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaint',
            name='departments',
            field=models.ManyToManyField(blank=True, related_name='complaints', to='departments.Department'),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='events',
            field=models.ManyToManyField(blank=True, related_name='complaints', to='officers.Event'),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='officers',
            field=models.ManyToManyField(blank=True, related_name='complaints', to='officers.Officer'),
        ),
    ]
