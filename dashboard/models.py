from django.db import models

# from dashboard.enums import WidgetsEnum
from django.utils.translation import gettext_lazy as _

from dashboard.enums import WidgetsEnum
from users.models import User


class SubscribedWidget(models.Model):
    """
    a reference to DashBoardWidget that is stored in the database
    for each user. so that they persist
    """

    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, related_name="widgets"
    )
    user_given_name = models.CharField(max_length=50)
    widget = models.CharField(
        _("Widget"),
        max_length=100,
        choices=WidgetsEnum.choices,
    )
