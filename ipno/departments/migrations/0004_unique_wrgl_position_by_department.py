# Generated by Django 3.1.4 on 2021-03-01 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0003_wrglfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wrglfile',
            name='position',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterUniqueTogether(
            name='wrglfile',
            unique_together={('department', 'position')},
        ),
    ]
