import itertools
from django.db.models import ProtectedError, RestrictedError
from drf_standardized_errors.handler import ExceptionHandler, exception_handler
from drf_standardized_errors.types import ExceptionHandlerContext, ErrorType
from drf_standardized_errors.formatter import ExceptionFormatter
from rest_framework.response import Response


def extended_exception_handler(exc: Exception, context: ExceptionHandlerContext):
    if isinstance(exc, (RestrictedError, ProtectedError)):
        objects = getattr(exc, "restricted_objects", None) or getattr(
            exc, "protected_objects", None
        )
        return Response(
            status=423,
            data=f'Silmeye çalıştığınız obje/objeler şu objelerle bağlantılı ve aradaki bağlantı kaldırılmadan silinemez: {", ".join(map(str, itertools.islice(objects, 5)))}',
        )
    return exception_handler(exc, context)


# def _parse_objects(objects: set) -> dict[str, int]:
#     return {k.__name__: v for k, v in objects).items()}
