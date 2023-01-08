from django.urls import include, path
from rest_framework import routers

from stakeholder import views
from .bulk_urls import url_patterns

router = routers.SimpleRouter()
router.register("customers", views.CustomerViewset)
router.register("suppliers", views.SupplierViewset)
router.register("stakeholder-employee", views.StakeholderEmployeeViewset)


urlpatterns = [
    path("", include(router.urls)),
    path("bulk/", include(url_patterns)),
]
