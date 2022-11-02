from tqdm import tqdm

from django.db.models import Count

from departments.models import Department
from officers.models import Officer
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

    for department in tqdm(all_departments, desc='Update officer fraction'):
        fraction = department.officers.count()/max_officer_count

        department.officer_fraction = fraction
        department.save()


def calculate_complaint_fraction():
    all_officers = Officer.objects.all()
    max_complaint_count = Person.objects.order_by('-all_complaints_count').first().all_complaints_count

    for officer in tqdm(all_officers, desc='Update complaint fraction'):
        fraction = officer.person.all_complaints_count/max_complaint_count

        officer.complaint_fraction = fraction
        officer.save()
