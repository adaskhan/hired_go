from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from jobs.views import CustomValidationFailed


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, CustomValidationFailed):
        response = Response(data=exc.args[0], status=status.HTTP_400_BAD_REQUEST)

    return response
