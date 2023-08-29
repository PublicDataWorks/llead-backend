from django.db.models import Count

from departments.models import OfficerMovement
from post_officer_history.models import PostOfficerHistory


class MigrateOfficerMovement:  # pragma: no cover
    def process(self):
        OfficerMovement.objects.all().delete()

        duplicate_histories = (
            PostOfficerHistory.objects.values_list("history_id", flat=True)
            .annotate(history_count=Count("history_id"))
            .filter(history_count__gt=1)
        )

        officer_movements = []

        for history_id in duplicate_histories:
            histories = PostOfficerHistory.objects.filter(
                history_id=history_id
            ).order_by("hire_date")

            for index in range(0, len(histories) - 1):
                officer_movement = OfficerMovement(
                    start_department=histories[index].department,
                    end_department=histories[index + 1].department,
                    officer=histories[index].officer,
                    date=histories[index + 1].hire_date,
                    left_reason=histories[index].left_reason,
                )
                officer_movements.append(officer_movement)

        OfficerMovement.objects.bulk_create(officer_movements)
