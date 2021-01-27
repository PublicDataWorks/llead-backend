# Generated by Django 3.1.4 on 2021-01-22 08:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('departments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Officer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('uid', models.CharField(max_length=255)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('middle_name', models.CharField(blank=True, max_length=255, null=True)),
                ('middle_initial', models.CharField(blank=True, max_length=255, null=True)),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('employee_id', models.CharField(blank=True, max_length=255, null=True)),
                ('birth_year', models.IntegerField()),
                ('birth_month', models.IntegerField()),
                ('birth_day', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OfficerHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('badge_no', models.CharField(blank=True, max_length=255, null=True)),
                ('rank_code', models.CharField(blank=True, max_length=255, null=True)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='departments.department')),
                ('officer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='officers.officer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='officer',
            name='departments',
            field=models.ManyToManyField(through='officers.OfficerHistory', to='departments.Department'),
        ),
    ]