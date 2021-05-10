from django.db import migrations
from django.utils.text import slugify


def generate_department_slug_data(apps, _):
    Department = apps.get_model('departments', 'Department')
    for department in Department.objects.all():
        department.slug = slugify(department.name)
        department.save()


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0007_department_slug'),
    ]

    operations = [
        migrations.RunPython(
            generate_department_slug_data,
            migrations.RunPython.noop
        ),
    ]
