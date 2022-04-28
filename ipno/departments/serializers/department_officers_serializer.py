from rest_framework import serializers

from shared.serializers import SimpleDepartmentSerializer


class DepartmentOfficerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    is_starred = serializers.BooleanField(default=False)
    use_of_forces_count = serializers.IntegerField()

    badges = serializers.SerializerMethodField()
    complaints_count = serializers.SerializerMethodField()
    departments = serializers.SerializerMethodField()
    latest_rank = serializers.SerializerMethodField()

    def _get_person_officers(self, obj):
        if not hasattr(obj, 'person_officers'):
            person_officers = obj.person.officers.all()
            setattr(
                obj,
                'person_officers',
                person_officers
            )

        return obj.person_officers

    def _get_all_events(self, obj):
        if not hasattr(obj, 'all_events'):
            all_officers = self._get_person_officers(obj)

            all_events = []
            for officer in all_officers:
                all_events.extend(officer.events.all())

            all_events.sort(key=lambda k: (-k.year, -k.month, -k.day))

            setattr(
                obj,
                'all_events',
                all_events
            )

        return obj.all_events

    def get_badges(self, obj):
        events = self._get_all_events(obj)

        events = list(dict.fromkeys([
            event.badge_no for event in events if event.badge_no
        ]))

        return events

    def get_complaints_count(self, obj):
        return obj.person.all_complaints_count

    def get_departments(self, obj):
        all_officers = self._get_person_officers(obj)

        departments = set()
        for officer in all_officers:
            departments.update(list(set(officer.departments.all())))

        return SimpleDepartmentSerializer(departments, many=True).data

    def get_latest_rank(self, obj):
        events = self._get_all_events(obj)

        rank_events = [rank for rank in events if rank.rank_desc]

        return rank_events[0].rank_desc if rank_events else None
