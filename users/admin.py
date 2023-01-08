from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from users.models import User


# Register your models here.
class UserAdmin(SimpleHistoryAdmin):
    list_display = (
        "username",
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )
    list_filter = ['is_superuser', 'is_staff', 'date_joined', 'is_active']


admin.site.register(User, UserAdmin)

