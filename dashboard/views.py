from django.http.response import JsonResponse
from rest_framework import permissions
from rest_framework.request import HttpRequest
from rest_framework.views import APIView
from dashboard.widgets import WIDGETMAP, gather_widgets_data
from asgiref.sync import async_to_sync

from users.models import User


async def get_widget_data(user: User) -> dict:
    widgets = user.widgets.all()
    widget_instances = []

    widget_name_map = {}
    async for widget in widgets:
        widget_name = f"{widget.widget}_{widget.id}"
        widget_instances.append(WIDGETMAP[widget.widget](widget_name))
        widget_name_map[widget_name] = widget.widget

    data = await gather_widgets_data(*widget_instances)
    return {"widget_data": data, "widget_name_map": widget_name_map}


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: HttpRequest):
        data = async_to_sync(get_widget_data)(request.user)
        return JsonResponse(data)
