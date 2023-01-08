from django.db import models
from django.utils import timezone

# from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as lazy

from users.models import User
from rest_framework import serializers


class CreateUpdateInfo(models.Model):
    created_by: User = models.ForeignKey(
        User,
        verbose_name=lazy("Oluşturan"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="created_%(class)s",
    )
    updated_by: User = models.ForeignKey(
        User,
        verbose_name=lazy("Değiştiren"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="updated_%(class)s",
    )
    created_at: timezone = models.DateTimeField(
        default=timezone.now, verbose_name=lazy("Oluşturma Tarihi")
    )
    updated_at: timezone = models.DateTimeField(
        verbose_name=lazy("Değiştirme Tarihi"), auto_now=True, null=True, blank=True
    )

    class Meta:
        abstract = True
