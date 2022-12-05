from django.apps import AppConfig


class QAndA(AppConfig):
    name = "q_and_a"

    def ready(self):
        import q_and_a.signals  # noqa
