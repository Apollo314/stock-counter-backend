from typing import Generic, TypeVar

from django.db import models
from django.utils import timezone
# from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from users.models import User


class CreateUpdateInfo(models.Model):
    created_by: User = models.ForeignKey(
        User,
        verbose_name=_("Created by"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="created_%(class)s",
        editable=False,
    )
    updated_by: User = models.ForeignKey(
        User,
        verbose_name=_("Updated by"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="updated_%(class)s",
    )
    created_at: timezone = models.DateTimeField(
        verbose_name=_("Created at"),
        auto_now_add=True,
        blank=True,
        null=True,
    )
    updated_at: timezone = models.DateTimeField(
        verbose_name=_("Updated at"), auto_now=True, null=True, blank=True
    )

    class Meta:
        abstract = True


class FilterOutInactiveObjectsManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(inactivated=False)
        return queryset


class FilterOutActiveObjectsManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(inactivated=True)
        return queryset


T = TypeVar("T")


class InactivatedMixin(models.Model, Generic[T]):
    """creates a field called inactivated and two managers to filter them.
    managers are called active_objects and inactive_objects, also has objects manager
    which doesn't do filtering.
    default manager is active_objects."""

    inactivated: bool = models.BooleanField(_("Inactivated"), default=False)

    active_objects = FilterOutInactiveObjectsManager[T]()
    inactive_objects = FilterOutActiveObjectsManager[T]()
    objects = models.Manager[T]()

    class Meta:
        abstract = True
