from django.urls import path

from stakeholder import bulkviews

url_patterns = [
    path("stakeholder/", bulkviews.BulkStakeholderViews.as_view()),
]
