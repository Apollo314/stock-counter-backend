from django.urls import include, path

from dashboard.views import DashboardView, SubscribedWidgetViewset

from rest_framework import routers

router = routers.SimpleRouter()
router.register("subscribed_widgets", SubscribedWidgetViewset)

urlpatterns = [
    path("", include(router.urls)),
    path("", DashboardView.as_view(), name="dashboard"),
]
