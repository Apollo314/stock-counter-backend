import logging

from drf_spectacular.extensions import (OpenApiFilterExtension,
                                        OpenApiSerializerFieldExtension)
from drf_spectacular.openapi import AutoSchema as AutoSchema_
from drf_spectacular.plumbing import ResolvedComponent

logger = logging.getLogger(__name__)


def build_media_type_object(schema, examples=None):
    if type(schema) == list:
        media_type_object = {"schema": {"anyOf": schema}}
    else:
        media_type_object = {"schema": schema}
    if examples:
        media_type_object["examples"] = examples
    return media_type_object


class AutoSchema(AutoSchema_):

    pass
    # def get_tags(self) -> typing.List[str]:
    #   """ override this for custom behaviour """
    #   tokenized_path = self._tokenize_path()
    #   return ['/'.join(tokenized_path)]

    # for custom field

    def resolve_serializer(
        self, serializer, direction, bypass_extensions=False
    ) -> ResolvedComponent:
        result = super().resolve_serializer(serializer, direction, bypass_extensions)
        if result.schema:
            if hasattr(serializer, "field_overrides"):
                field_overrides = serializer.field_overrides
                for key, override in field_overrides.items():
                    try:
                        result.schema["properties"][key]["x-components"] = override
                    except Exception as ex:
                        logger.exception(ex)
                return result
        return result

    def _get_filters(self) -> dict:
        filters = dict()
        for filter_backend in self.get_filter_backends():
            filter_extension = OpenApiFilterExtension.get_match(filter_backend())
            if filter_extension:
                filters[
                    filter_backend.__name__
                ] = filter_extension.get_schema_operation_parameters(self)
            else:
                filters[
                    filter_backend.__name__
                ] = filter_backend().get_schema_operation_parameters(self.view)
        return filters

    def get_operation(self, path, path_regex, path_prefix, method, registry):
        operation = super().get_operation(
            path, path_regex, path_prefix, method, registry
        )
        if self._is_list_view():
            operation["x-filters"] = self._get_filters()
        return operation

    # this exist because drf_spectacular for some reason,
    # thinks it's fine to remove title if it field.field_name and field.label
    # resembles each other.
    def _get_serializer_field_meta(self, field, direction):
        result = super()._get_serializer_field_meta(field, direction)
        result["title"] = field.label
        return result
