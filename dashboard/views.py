import asyncio
from django.http.response import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.request import HttpRequest
from rest_framework.views import APIView
from dashboard.serializers import DashboardSerializer
from dashboard.widgets import WIDGETMAP, Widget
from asgiref.sync import async_to_sync, sync_to_async

from users.models import User


async def gather_widgets_data(*widgets: Widget):
    """takes widgets, asyncronously queries their querysets, returns them in a dict
    with the unique_name of the widget as the key"""

    # result = defaultdict(list)
    result = []

    async def task(widget: Widget):
        queryset = widget.get_queryset()
        instances = []
        async for instance in queryset:
            instances.append(instance)

        widget_data = await sync_to_async(widget.serialized_data)(instances)
        subscribed_widget = widget.subscribed_widget
        result.append(
            {
                "id": subscribed_widget.id,
                "widget_index": subscribed_widget.widget_index,
                "user_settings": subscribed_widget.user_settings,
                "widget_name": subscribed_widget.widget_name,
                "widget_data": widget_data,
            }
        )

    await asyncio.gather(*(task(widget) for widget in widgets))
    return result


async def get_widget_data(user: User) -> dict:
    subscribed_widgets = user.widgets.all()
    widget_instances = []

    async for subscribed_widget in subscribed_widgets:
        widget_instances.append(
            WIDGETMAP[subscribed_widget.widget_name](subscribed_widget)
        )

    data = await gather_widgets_data(*widget_instances)
    return data


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: DashboardSerializer(many=True)})
    def get(self, request: HttpRequest):
        data = async_to_sync(get_widget_data)(request.user)
        return JsonResponse(data, safe=False)
