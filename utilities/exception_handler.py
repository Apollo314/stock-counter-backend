import itertools

from django.db.models import ProtectedError, RestrictedError
from drf_standardized_errors.handler import exception_handler
from drf_standardized_errors.types import ExceptionHandlerContext
from rest_framework.exceptions import APIException, status


class ProtectedAPIException(APIException):
    """Because this is something the end user can actually see, it shouldn't return 500
    like the default behavior. Will replace ProtectedError"""

    status_code = status.HTTP_423_LOCKED


class RestrictedAPIException(APIException):
    """Because this is something the end user can actually see, it shouldn't return 500
    like the default behavior. Will replace RestrictedError"""

    status_code = status.HTTP_423_LOCKED


def extended_exception_handler(exc: Exception, ctx: ExceptionHandlerContext):
    if isinstance(exc, (RestrictedError, ProtectedError)):
        if isinstance(exc, RestrictedError):
            exc = RestrictedAPIException(str(exc))
        elif isinstance(exc, ProtectedError):
            exc = ProtectedAPIException(str(exc))
    return exception_handler(exc, ctx)
