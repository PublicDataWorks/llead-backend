from django.apps import AppConfig


class Department(AppConfig):
    name = 'departments'

    def ready(self):
        import departments.signals # noqa