from django.db import models


def handle_file_field_cleanup_pre_save(
    sender: models.Model, instance: models.Model, **kwargs
):
    if instance.pk:
        try:
            old_instance: models.Model = sender._default_manager.get(pk=instance.pk)
        except sender.DoesNotExist:
            return
        else:
            file_fields = [
                field.name
                for field in instance._meta.fields
                if isinstance(field, models.FileField)
            ]
            for field_name in file_fields:
                new_field: models.FileField = getattr(instance, field_name)
                old_field = getattr(old_instance, field_name)
                if old_field:
                    if not new_field:
                        old_field.delete(save=False)
                    elif old_field.url != new_field.url:
                        old_field.delete(save=False)


def handle_file_pre_delete(sender: models.Model, instance: models.Model, **kwargs):
    file_fields = [
        field.name
        for field in instance._meta.fields
        if isinstance(field, models.FileField)
    ]
    for field_name in file_fields:
        field = getattr(instance, field_name)
        if field:
            field.delete(save=False)
