from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.request import HttpRequest
from rest_framework.response import Response


class BulkPatchMixin:
    def __init_subclass__(
        cls,
        **kwargs,
    ) -> None:
        request_serializer = (
            cls.request_serializer
            if hasattr(cls, "request_serializer")
            else cls.serializer_class
        )

        extend_schema(
            parameters=[
                OpenApiParameter(
                    name=cls.lookup_field,
                    required=True,
                    type={"type": "array", "items": {"type": "string"}},
                ),
            ],
            request=request_serializer(many=True, partial=True),
        )(getattr(cls, "patch"))
        super().__init_subclass__(**kwargs)

    def patch(self, request: HttpRequest, *args, **kwargs):
        lookup_identifiers = request.query_params.getlist(self.lookup_field)
        queryset: QuerySet = self.queryset.filter(
            **{f"{self.lookup_field}__in": lookup_identifiers}
        )
        serializer = self.get_serializer(
            queryset, data=request.data, partial=True, many=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class BulkDeleteMixin:
    def __init_subclass__(
        cls,
        lookup_field="pk",
        **kwargs,
    ) -> None:
        cls.lookup_field = lookup_field

        extend_schema(
            parameters=[
                OpenApiParameter(
                    name=lookup_field,
                    required=True,
                    type={"type": "array", "items": {"type": "string"}},
                ),
            ],
        )(getattr(cls, "delete"))
        super().__init_subclass__(**kwargs)

    def delete(self, request, *args, **kwargs):
        lookup_identifiers = request.query_params.getlist(self.lookup_field)
        queryset: QuerySet = self.queryset.filter(
            **{f"{self.lookup_field}__in": lookup_identifiers}
        )
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

