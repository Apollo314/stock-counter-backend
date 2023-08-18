from datetime import datetime

from django.db import models
from django_filters import fields, filters, filterset
from django_filters.rest_framework import DjangoFilterBackend as _DjangoFilterBackend
from drf_spectacular.plumbing import follow_model_field_lookup
from rest_framework.filters import OrderingFilter as _OrderingFilter
from rest_framework.filters import SearchFilter as _SearchFilter


class OrderingFilter(_OrderingFilter):
    def get_schema_operation_parameters(self, view):
        result = super().get_schema_operation_parameters(view)
        valid_fields = getattr(view, "ordering_fields", self.ordering_fields)
        result[0]["schema"]["enum"] = valid_fields + [
            f"-{field}" for field in valid_fields
        ]
        return result


class SearchFilter(_SearchFilter):
    def get_schema_operation_parameters(self, view):
        result = super().get_schema_operation_parameters(view)
        search_fields = getattr(view, "search_fields", None)
        serializer = view.get_serializer()
        model = serializer.Meta.model
        search_fields_verbose = [
            str(follow_model_field_lookup(model, name).verbose_name)
            for name in search_fields
        ]
        description = f'Ara: {", ".join(search_fields_verbose)}'
        result[0]["description"] = description
        return result


class BetterDateRangeField(filters.BaseCSVFilter):
    base_field_class = fields.BaseRangeField

    def filter(self, qs, value):
        if value:
            start = datetime.strptime(value[0].strip(), "%Y-%m-%d")
            end = datetime.strptime(value[1].strip(), "%Y-%m-%d").replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
            value = [start, end]
        return super().filter(qs, value)


class FilterSet(filterset.FilterSet):
    @classmethod
    def filter_for_lookup(cls, f, lookup_type):
        # override date range lookups
        if isinstance(f, models.DateField) and lookup_type == "range":
            return BetterDateRangeField, {}

        return super().filter_for_lookup(f, lookup_type)


class DjangoFilterBackend(_DjangoFilterBackend):
    filterset_base = FilterSet

    def get_schema_operation_parameters(self, view):
        try:
            queryset = view.get_queryset()
        except Exception:
            queryset = None

        filterset_class = self.get_filterset_class(view, queryset)

        if not filterset_class:
            return []

        filterset_fields = getattr(
            view, "filterset_fields", filterset_class.Meta.fields
        )
        filterset_overrides = getattr(view, "filterset_overrides", {})
        parameters = []
        for field_name, field in filterset_class.base_filters.items():
            separator_index = field_name.rfind("__")
            if separator_index != -1:
                key, lookup = (
                    field_name[:separator_index],
                    field_name[separator_index + 2 :],
                )
                if lookup not in [
                    "iexact",
                    "contains",
                    "icontains",
                    "in",
                    "gt",
                    "gte",
                    "lt",
                    "lte",
                    "startswith",
                    "istartswith",
                    "endswith",
                    "iendswith",
                    "date",
                    "year",
                    "iso_year",
                    "month",
                    "day",
                    "week",
                    "week_day",
                    "iso_week_day",
                    "quarter",
                    "time",
                    "hour",
                    "minute",
                    "second",
                    "regex",
                    "iregex",
                    "range",
                    "isnull",
                    "notin",  # custom, not conventional
                ]:
                    key += "__" + lookup
                    lookup = "exact"
            else:
                key = field_name
                lookup = "exact"
            parameter = {
                "name": field_name,
                "required": field.extra["required"],
                "in": "query",
                "description": field.label if field.label is not None else field_name,
                "schema": {
                    "type": "string",
                    "x-components": filterset_fields.get(key, {}).get(lookup, None)
                    or filterset_overrides.get(key, {}).get(lookup, None),
                },
            }
            if field.extra and "choices" in field.extra:
                parameter["schema"]["enum"] = [c[0] for c in field.extra["choices"]]
            parameters.append(parameter)
        return parameters

    def get_filterset_kwargs(self, request, queryset, view):
        # can handle queries like these:
        # somepath/?id=2&id=3&id=4
        # without this id=4 overrides the others as if they don't exist.
        query_params = request.query_params
        params = {}
        for param in query_params:
            if len(paramlist := query_params.getlist(param)) > 1:
                params[param] = ",".join(paramlist)
            else:
                params[param] = query_params.get(param)

        return {
            "data": params,
            "queryset": queryset,
            "request": request,
        }
