# Generated by Django 3.1.4 on 2021-03-01 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('officers', '0006_update_fields_for_officer_history'),
    ]

    operations = [
        migrations.AlterField(
            model_name='officer',
            name='birth_day',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='officer',
            name='birth_month',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='officer',
            name='birth_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='officerhistory',
            name='data_production_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='officerhistory',
            name='hire_day',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='officerhistory',
            name='hire_month',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='officerhistory',
            name='hire_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='officerhistory',
            name='pay_effective_day',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='officerhistory',
            name='pay_effective_month',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='officerhistory',
            name='pay_effective_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='officerhistory',
            name='term_day',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='officerhistory',
            name='term_month',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='officerhistory',
            name='term_year',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
