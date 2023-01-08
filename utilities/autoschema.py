from drf_spectacular.extensions import OpenApiFilterExtension
from drf_spectacular.openapi import AutoSchema as AutoSchema_


def build_media_type_object(schema, examples=None):
    if type(schema) == list:
        media_type_object = {"schema": {"anyOf": schema}}
    else:
        media_type_object = {"schema": schema}
    if examples:
        media_type_object["examples"] = examples
    return media_type_object


class AutoSchema(AutoSchema_):
    # def get_tags(self) -> typing.List[str]:
    #   """ override this for custom behaviour """
    #   tokenized_path = self._tokenize_path()
    #   return ['/'.join(tokenized_path)]

    # for custom field
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
