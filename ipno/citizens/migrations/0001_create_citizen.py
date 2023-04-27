# Generated by Django 3.1.13 on 2023-02-19 09:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('complaints', '0016_remove_dispensable_fields'),
        ('use_of_forces', '0009_delete_useofforcecitizen'),
        ('departments', '0023_rename_fields_name_and_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='Citizen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('citizen_uid', models.CharField(max_length=255)),
                ('allegation_uid', models.CharField(blank=True, max_length=255, null=True)),
                ('uof_uid', models.CharField(blank=True, max_length=255, null=True)),
                ('citizen_influencing_factors', models.CharField(blank=True, max_length=255, null=True)),
                ('citizen_arrested', models.CharField(blank=True, max_length=255, null=True)),
                ('citizen_hospitalized', models.CharField(blank=True, max_length=255, null=True)),
                ('citizen_injured', models.CharField(blank=True, max_length=255, null=True)),
                ('citizen_age', models.IntegerField(blank=True, null=True)),
                ('citizen_race', models.CharField(blank=True, max_length=255, null=True)),
                ('citizen_sex', models.CharField(blank=True, max_length=255, null=True)),
                ('agency', models.CharField(blank=True, max_length=255, null=True)),
                ('complaint', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='citizens', to='complaints.complaint')),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='citizens', to='departments.department')),
                ('use_of_force', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='citizens', to='use_of_forces.useofforce')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]