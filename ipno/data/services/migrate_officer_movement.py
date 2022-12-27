from django.db.models import Prefetch, Sum
from django.db.models.expressions import Case, F, When
from django.db.models.fields import IntegerField

from departments.models import OfficerMovement
from officers.constants import OFFICER_HIRE, OFFICER_LEFT
from officers.models import Event, Officer
from people.models import Person
from utils.parse_utils import parse_date


class MigrateOfficerMovement:
    def process(self):
        OfficerMovement.objects.all().delete()
        officer_movements = []

        have_left_hire_officers = Officer.objects.annotate(
            left_count=Sum(
                Case(
                    When(events__kind=OFFICER_LEFT, then=1), output_field=IntegerField()
                )
            ),
            hire_count=Sum(
                Case(
                    When(events__kind=OFFICER_HIRE, then=1), output_field=IntegerField()
                )
            ),
        ).filter(left_count__gt=0, hire_count__gt=0)

        people = (
            Person.objects.prefetch_related(
                "officers",
                Prefetch(
                    "officers__events",
                    queryset=Event.objects.order_by(
                        F("year").desc(nulls_last=True),
                        F("month").desc(nulls_last=True),
                        F("day").desc(nulls_last=True),
                    )
                    .filter(
                        kind__in=[OFFICER_LEFT, OFFICER_HIRE],
                        department__location__isnull=False,
                    )
                    .select_related("officer", "department"),
                    to_attr="prefetch_hire_left_events",
                ),
            )
            .filter(officers__in=have_left_hire_officers)
            .distinct()
        )

        for person in people:
            officers = person.officers.all()
            hire_left_events = {}

            for officer in officers:
                hire_left_officer_events = officer.prefetch_hire_left_events
                for event in hire_left_officer_events:
                    event_date = parse_date(event.year, event.month, event.day)

                    if (
                        event_date
                        and (event.officer.id, event_date, event.kind)
                        not in hire_left_events
                    ):
                        hire_left_events[(event.officer.id, event_date, event.kind)] = (
                            event_date,
                            event,
                        )

            hire_left_dates = list(hire_left_events.values())
            hire_left_dates.sort(key=lambda x: (x[0], x[1].event_uid))
            lines = []

            for index in range(0, len(hire_left_dates) - 1):
                if (
                    hire_left_dates[index][1].department
                    != hire_left_dates[index + 1][1].department
                    and hire_left_dates[index][1].kind == OFFICER_LEFT
                    and hire_left_dates[index + 1][1].kind == OFFICER_HIRE
                ):
                    lines.append((hire_left_dates[index], hire_left_dates[index + 1]))

            if len(lines) > 0:
                for line in lines:
                    officer_movement = OfficerMovement(
                        start_department=line[0][1].department,
                        end_department=line[1][1].department,
                        officer=line[0][1].officer,
                        date=line[1][0],
                        left_reason=line[0][1].left_reason,
                    )
                    officer_movements.append(officer_movement)

        OfficerMovement.objects.bulk_create(officer_movements)
