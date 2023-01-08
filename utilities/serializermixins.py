from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import Field
from rest_framework.validators import UniqueValidator


class UniqueFieldsMixin(serializers.ModelSerializer):
    # Moves `UniqueValidator`'s from the validation stage to the save stage.
    # It solves the problem with nested validation for unique fields on update.
    # If you want more details, you can read related issues and articles:
    # https://github.com/beda-software/drf-writable-nested/issues/1
    # http://www.django-rest-framework.org/api-guide/validators/#updating-nested-serializers
    # Example of usage:
    # ```
    # class Child(models.Model):
    #   field = models.CharField(unique=True)
    # class Parent(models.Model):
    #   child = models.ForeignKey('Child')
    # class ChildSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    #   class Meta:
    #     model = Child
    # class ParentSerializer(NestedUpdateMixin, serializers.ModelSerializer):
    #   child = ChildSerializer()
    #   class Meta:
    #     model = Parent
    # ```
    # Note: `UniqueFieldsMixin` must be applied only on the serializer
    # which has unique fields.
    # Note: When you are using both mixins
    # (`UniqueFieldsMixin` and `NestedCreateMixin` or `NestedUpdateMixin`)
    # you should put `UniqueFieldsMixin` ahead.

    _unique_fields: list[tuple[str, UniqueValidator]] = []

    def get_fields(self):
        self._unique_fields = []

        fields: dict[str, Field] = super(UniqueFieldsMixin, self).get_fields()
        for field_name, field in fields.items():
            unique_validators = [
                validator
                for validator in field.validators
                if isinstance(validator, UniqueValidator)
            ]
            if unique_validators:
                # 0 means only take the first one UniqueValidator
                self._unique_fields.append((field_name, unique_validators[0]))
                field.validators = [
                    validator
                    for validator in field.validators
                    if not isinstance(validator, UniqueValidator)
                ]

        return fields

    def _validate_unique_fields(self, validated_data):
        for unique_field in self._unique_fields:
            field_name, unique_validator = unique_field
            if self.partial and field_name not in validated_data:
                continue
            try:
                # `set_context` removed on DRF >= 3.11, pass in via __call__ instead
                if hasattr(unique_validator, "set_context"):
                    unique_validator.set_context(self.fields[field_name])
                    unique_validator(validated_data[field_name])
                else:
                    unique_validator(
                        validated_data[field_name], self.fields[field_name]
                    )
            except ValidationError as exc:
                raise ValidationError({field_name: exc.detail})

    def create(self, validated_data):
        self._validate_unique_fields(validated_data)
        return super(UniqueFieldsMixin, self).create(validated_data)

    def update(self, instance, validated_data):
        self._validate_unique_fields(validated_data)
        return super(UniqueFieldsMixin, self).update(instance, validated_data)
