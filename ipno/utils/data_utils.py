from tqdm import tqdm

from departments.models import Department
from officers.constants import COMPLAINT_ALL_EVENTS, UOF_ALL_EVENTS
from officers.models import Event


def format_data_period(years):
    results = []
    current_year = None

    for year in sorted(list(set(years))):
        if current_year and year == current_year + 1:
            results[-1].append(year)
        else:
            results.append([year])
        current_year = year

    return [f'{item[0]}{f"-{item[-1]}" if len(item) > 1 else ""}' for item in results]


def sort_items(items, attrs):
    def get_sort_key(item, item_attrs):
        results = []
        for attr in item_attrs:
            value = getattr(item, attr)
            results.append((value is None, str(value)))
        return results

    return sorted(items, key=lambda item: get_sort_key(item, attrs))


def compute_department_data_period():
    all_department = Department.objects.all()
    for department in tqdm(all_department, desc="Update department data period"):
        event_years = Event.objects.filter(
            department=department,
            kind__in=COMPLAINT_ALL_EVENTS + UOF_ALL_EVENTS,
        ).values_list("year", flat=True)

        sorted_event_years = sorted(list(set(event_years)))
        department.data_period = sorted_event_years

    Department.objects.bulk_update(all_department, ["data_period"])
