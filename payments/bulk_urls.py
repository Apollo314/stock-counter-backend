from django.urls import path

from payments import bulkviews

url_patterns = [
    path("payment-accounts/", bulkviews.BulkPaymentAccountViews.as_view()),
    path("payments/", bulkviews.BulkPaymentViews.as_view()),
    path("banks/", bulkviews.BulkBankViews.as_view()),
]
