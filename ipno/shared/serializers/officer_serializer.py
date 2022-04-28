from rest_framework import serializers

from shared.serializers import SimpleDepartmentSerializer


class OfficerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    badges = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    latest_rank = serializers.SerializerMethodField()

    def _get_all_events(self, obj):
        if not hasattr(obj, 'all_events'):
            all_officers = obj.person.officers.all()

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

    def get_department(self, obj):
        events = self._get_all_events(obj)
        if events and events[0]:
            return SimpleDepartmentSerializer(events[0].department).data

    def get_latest_rank(self, obj):
        events = self._get_all_events(obj)

        rank_events = [rank for rank in events if rank.rank_desc]

        return rank_events[0].rank_desc if rank_events else None
