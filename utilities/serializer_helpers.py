from rest_framework.serializers import SkipField


class CurrentUserCreatedBy:
    requires_context = True

    def __call__(self, serializer_field):
        is_update = serializer_field.parent.instance is not None
        if is_update:
            raise SkipField
        return serializer_field.context["request"].user

    def __repr__(self):
        return "%s()" % self.__class__.__name__


class CurrentUserDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context["request"].user

    def __repr__(self):
        return "%s()" % self.__class__.__name__
