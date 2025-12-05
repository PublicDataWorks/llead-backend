from rest_framework import serializers

from shared.serializers import SimpleDepartmentSerializer


class OfficerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    badges = serializers.SerializerMethodField()
    departments = serializers.SerializerMethodField()
    latest_rank = serializers.SerializerMethodField()

    def _get_all_events(self, obj):
        if not hasattr(obj, "all_events"):
            # Handle officers without person association
            if obj.person:
                all_officers = obj.person.officers.all()
            else:
                all_officers = [obj]

            all_events = []
            for officer in all_officers:
                all_events.extend(officer.events.all())

            all_events.sort(
                key=lambda k: (
                    (k.year is None, -k.year if k.year is not None else None),
                    (k.month is None, -k.month if k.month is not None else None),
                    (k.day is None, -k.day if k.day is not None else None),
                )
            )

            setattr(obj, "all_events", all_events)

        return obj.all_events

    def get_badges(self, obj):
        events = self._get_all_events(obj)

        events = list(
            dict.fromkeys([event.badge_no for event in events if event.badge_no])
        )

        return events

    def get_departments(self, obj):
        # Handle officers without person association
        canonical_dep = None
        if obj.person and obj.person.canonical_officer:
            canonical_dep = obj.person.canonical_officer.department

        all_events = self._get_all_events(obj)

        all_departments = {event.department for event in all_events}
        raw_departments = list(dict.fromkeys([canonical_dep, *all_departments]))
        departments = [
            department for department in raw_departments if department is not None
        ]

        return SimpleDepartmentSerializer(departments, many=True).data

    def get_latest_rank(self, obj):
        events = self._get_all_events(obj)

        rank_events = [rank for rank in events if rank.rank_desc]

        return rank_events[0].rank_desc if rank_events else None
