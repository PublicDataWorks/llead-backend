# Generated by Django 3.1.4 on 2021-09-03 07:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('use_of_forces', '0004_useofforce_citizen_uid'),
        ('departments', '0010_add_related_name_for_wrgl_file_relations'),
        ('officers', '0021_remove_event_allegation_uid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to='departments.department'),
        ),
        migrations.AlterField(
            model_name='event',
            name='use_of_force',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to='use_of_forces.useofforce'),
        ),
    ]
