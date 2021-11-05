from tqdm import tqdm

from people.models import Person


def count_complaints():
    for person in tqdm(Person.objects.all(), desc='Update person complaints count'):
        complaints_list = set()

        for officer in person.officers.all():
            complaints_list.update(set(officer.complaints.all()))

        person.all_complaints_count = len(complaints_list)
        person.save()
