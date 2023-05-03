from django.urls import include, path
from rest_framework import routers

from invoice import views

from .bulk_urls import url_patterns

router = routers.SimpleRouter()
router.register("invoice", views.InvoiceViewset)
router.register("invoice-conditions", views.InvoiceConditionTemplateViewset)
# router.register('invoice-item', views.InvoiceItemViewset)


urlpatterns = [
    path("", include(router.urls)),
    path("bulk/", include(url_patterns)),
]
