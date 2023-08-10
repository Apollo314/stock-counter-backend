from pathlib import Path

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


def get_profile_image_location(instance: "User", filename: str):
    f = Path(filename)
    path = Path("user_images") / f"{instance.username}_{f.suffix}"
    return path


class User(AbstractUser):
    phone = models.CharField(_("Phone"), max_length=15, null=True, blank=True)
    avatar = models.ImageField(
        _("User profile picture"),
        upload_to=get_profile_image_location,
        null=True,
        blank=True,
    )
    email = models.EmailField(_("email address"))
