from django.urls import path

from invoice import bulkviews

url_patterns = [
    path("invoice/", bulkviews.BulkInvoiceViews.as_view()),
]
