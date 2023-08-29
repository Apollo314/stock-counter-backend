from django.apps import AppConfig


class StakeholderConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "stakeholder"

    def ready(self):
        from stakeholder import signals  # noqa: F401
