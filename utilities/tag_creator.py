from drf_spectacular.utils import extend_schema


def create_tags_for_methods(tags: list["str"], *methods: list["str"]):
    """__all__ would create get, list, post, patch and delete"""
    if methods[0] == "__all__":
        methods = ["retrieve", "list", "create", "update", "partial_update", "destroy"]
    return {method: extend_schema(tags=tags) for method in methods}
