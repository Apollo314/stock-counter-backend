from django.contrib.auth.models import AbstractUser
from django.db import models
from pathlib import Path
from django.forms import ImageField


def get_profile_image_location(instance: "User", filename: str):
    f = Path(filename)
    path = Path("user_images") / f"{instance.username}_{instance.id}{f.suffix}"
    return path


class User(AbstractUser):
    phone = models.CharField("Telefon", max_length=15, null=True, blank=True)
    avatar: ImageField = models.ImageField(
        "Kullanıcı Resmi", upload_to=get_profile_image_location, null=True, blank=True
    )
