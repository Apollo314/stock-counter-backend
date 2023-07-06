from django.urls import include, path
from rest_framework import routers

from payments import views

router = routers.SimpleRouter()
router.register("banks", views.BankViewset)
router.register("payment-accounts", views.PaymentAccountViewset)


urlpatterns = [
    path("", include(router.urls)),
]
