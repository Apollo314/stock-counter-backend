from django.apps import AppConfig


class InvoiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "invoice"

    def ready(self):
        from invoice import signals as _
