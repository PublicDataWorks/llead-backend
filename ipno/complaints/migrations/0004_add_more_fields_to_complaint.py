# Generated by Django 3.1.4 on 2021-04-22 04:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('complaints', '0003_allow_blank_for_complaint_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='allegation',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='allegation_class',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='allegation_finding',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='allegation_uid',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='app_used',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='assigned_department',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='assigned_division',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='assigned_sub_division_a',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='assigned_unit',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='badge_no',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='body_worn_camera_available',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='charge_uid',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='charges',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='citizen',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='citizen_arrested',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='complainant_race',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='complaint_uid',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='department_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='department_desc',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='incident_type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='investigation_type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='rank_desc',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='complaint',
            name='recommended_action',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='data_production_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='complaint',
            unique_together={('complaint_uid', 'allegation_uid', 'charge_uid')},
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='complainant_name',
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='incident_date',
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='occur_day',
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='occur_month',
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='occur_time',
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='occur_year',
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='receive_day',
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='receive_month',
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='receive_year',
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='suspension_end_day',
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='suspension_end_month',
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='suspension_end_year',
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='suspension_start_day',
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='suspension_start_month',
        ),
        migrations.RemoveField(
            model_name='complaint',
            name='suspension_start_year',
        ),
    ]
