from django.urls import path

from users import bulkviews

url_patterns = [
    path("groups/", bulkviews.BulkGroupView.as_view()),
    path("accounts/", bulkviews.BulkAccountView.as_view()),
]
