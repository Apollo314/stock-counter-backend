from django.urls import include, path
from rest_framework import routers

from payments import views

router = routers.SimpleRouter()
router.register("banks", views.BankViewset)
router.register(
    "payment-accounts", views.PaymentAccountViewset, basename="payment-accounts"
)
router.register("payments", views.PaymentViewset, basename="payments")
router.register(
    "invoice-payments", views.InvoicePaymentViewset, basename="invoice-payments"
)


urlpatterns = [
    path("", include(router.urls)),
]
