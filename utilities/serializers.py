# so apparently modelserializers just don't care about model field defaults in openapi documentation
# not anymore.
# good to have for autoform generation.

# also if blank=False, field should be required

from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ListSerializer
from rest_framework.serializers import ModelSerializer as ModelSerializer_

from django.db import models, IntegrityError
from drf_extra_fields import fields

serializer_field_mapping_override = {
    models.ImageField: fields.Base64ImageField,
}


class ModelSerializer(ModelSerializer_):
    serializer_field_mapping = {
        **ModelSerializer_.serializer_field_mapping,
        **serializer_field_mapping_override,
    }

    def build_standard_field(self, field_name, model_field):
        field_class, field_kwargs = super().build_standard_field(
            field_name, model_field
        )
        if model_field.has_default():
            field_kwargs["default"] = model_field.default
        elif not (model_field.blank):
            field_kwargs["required"] = True
        return (field_class, field_kwargs)

    def build_relational_field(self, field_name, relation_info):
        field_class, field_kwargs = super().build_relational_field(
            field_name, relation_info
        )
        (
            model_field,
            related_model,
            to_many,
            to_field,
            has_through_model,
            reverse,
        ) = relation_info
        if not getattr(model_field, "blank", False):
            field_kwargs["required"] = True
        return (field_class, field_kwargs)


class DynamicFieldsModelSerializer(ModelSerializer):
    def __init__(
        self,
        *args,
        included_fields: list[str] | None = None,
        excluded_fields: list["str"] | None = None,
        **kwargs
    ):

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if included_fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(included_fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        elif excluded_fields is not None:
            existing = set(self.fields.keys())
            notallowed = set(excluded_fields)
            for field_name in existing & notallowed:
                self.fields.pop(field_name)


class UpdateListSerializer(ListSerializer):
    def update(self, instances, validated_data_list):
        if instances.count() != len(validated_data_list):
            raise ValidationError({"message": "Amount of instances doesn't match data"})

        update_fields = []
        for (instance, validated_data) in zip(instances, validated_data_list):
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
                if attr not in update_fields:
                    update_fields.append(attr)

        self.child.Meta.model._default_manager.bulk_update(instances, update_fields)
        return instances


class CreateListSerializer(ListSerializer):
    def create(self, validated_data):
        result = [self.child.create(attrs) for attrs in validated_data]

        try:
            self.child.Meta.model.objects.bulk_create(result)
        except IntegrityError as e:
            raise ValidationError(e)

        return result
