from django.urls import include, path
from rest_framework import routers

from users import views
from users.bulk_urls import url_patterns as bulk_url_patterns
from users.knoxviews import LoginView, LogoutAllView, LogoutView

router = routers.SimpleRouter()
router.register("groups", views.GroupViewset)
router.register("accounts", views.UserViewset)


urlpatterns = [
    path("login/", LoginView.as_view(), name="knox_login"),
    path("logout/", LogoutView.as_view(), name="knox_logout"),
    path("logoutall/", LogoutAllView.as_view(), name="knox_logoutall"),
    path(
        "permissions/", views.PermissionListView.as_view(), name="permission_listview"
    ),
    path("me/", views.MyAccountView.as_view(), name="my_account"),
    path("bulk/", include(bulk_url_patterns)),
    path("", include(router.urls)),
]
