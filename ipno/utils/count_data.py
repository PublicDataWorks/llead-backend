from tqdm import tqdm

from django.db.models import Count

from departments.models import Department
from people.models import Person


def count_complaints():
    for person in tqdm(Person.objects.all(), desc='Update person complaints count'):
        complaints_list = set()

        for officer in person.officers.all():
            complaints_list.update(set(officer.complaints.all()))

        person.all_complaints_count = len(complaints_list)
        person.save()


def calculate_officer_fraction():
    all_departments = Department.objects.all()
    max_officer_count = Department.objects.annotate(
        officer_count=Count('officers')
    ).order_by('-officer_count').first().officer_count

    for department in tqdm(all_departments, desc='Update officer count percentage'):
        percentage = department.officers.count()/max_officer_count

        department.officer_fraction = percentage
        department.save()
