from django.db import models

# from dashboard.enums import WidgetsEnum
from django.utils.translation import gettext_lazy as _


# class SubscribedWidgets(models.Model):
#     """
#     a reference to DashBoardWidget that is stored in the database
#     for each user. so that they persist
#     """
#
#     user_given_name = models.CharField(max_length=50)
#     widget = models.CharField(
#         _("Widget"),
#         max_length=50,
#         choices=WidgetsEnum.choices,
#     )
