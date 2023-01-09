from django.urls import include, path
from rest_framework import routers

from users import views
from users.knoxviews import LoginView, LogoutAllView, LogoutView

router = routers.SimpleRouter()
# router.register("groups", views.GroupViewset)
router.register("accounts", views.UserViewset)


urlpatterns = [
    path("login/", LoginView.as_view(), name="knox_login"),
    path("logout/", LogoutView.as_view(), name="knox_logout"),
    path("logoutall/", LogoutAllView.as_view(), name="knox_logoutall"),
    path("groups/", views.GroupListView.as_view(), name="user_groups"),
    path("me/", views.MyAccountView.as_view(), name="my_account"),
    path("", include(router.urls)),
]
