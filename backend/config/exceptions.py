import logging
from django.core.exceptions import ValidationError as DjangoValidationError, PermissionDenied
from django.http import Http404
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    ValidationError as DRFValidationError,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied as DRFPermissionDenied,
    NotFound,
    MethodNotAllowed,
    Throttled,
)

logger = logging.getLogger('jobcare')


def custom_exception_handler(exc, context):
    if isinstance(exc, DjangoValidationError):
        exc = DRFValidationError(detail=exc.messages)

    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'success': False,
            'status_code': response.status_code,
            'message': _get_default_message(response.status_code),
            'errors': {},
        }

        if isinstance(response.data, dict):
            for field, messages in response.data.items():
                if isinstance(messages, list):
                    error_data['errors'][field] = [str(m) for m in messages if m]
                elif isinstance(messages, dict):
                    error_data['errors'][field] = str(messages)
                else:
                    error_data['errors'][field] = str(messages) if messages else ''
            first_error = _find_first_error(response.data)
            if first_error:
                error_data['message'] = first_error
        elif isinstance(response.data, list) and len(response.data) > 0:
            error_data['message'] = str(response.data[0])
        elif isinstance(response.data, str):
            error_data['message'] = response.data
        elif isinstance(exc, Throttled):
            error_data['message'] = f'Too many requests. Try again in {exc.wait} seconds.'
            error_data['retry_after'] = exc.wait

        return Response(error_data, status=response.status_code)

    logger.error(f'Unhandled exception: {exc}', exc_info=True)
    return Response(
        {
            'success': False,
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': 'An unexpected error occurred. Please try again later.',
            'errors': {},
            'error_id': getattr(exc, 'error_id', None),
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _get_default_message(status_code):
    messages = {
        400: 'Bad request. Please check your input.',
        401: 'Authentication required.',
        403: 'You do not have permission to perform this action.',
        404: 'Resource not found.',
        405: 'Method not allowed.',
        409: 'Conflict with current state.',
        429: 'Too many requests. Please slow down.',
        500: 'An unexpected error occurred.',
    }
    return messages.get(status_code, 'An error occurred.')


def _find_first_error(data):
    if isinstance(data, dict):
        for field, messages in data.items():
            if field == 'detail' and isinstance(messages, str):
                return messages
            if isinstance(messages, list) and len(messages) > 0:
                return str(messages[0])
            if isinstance(messages, str) and messages:
                return messages
            if isinstance(messages, dict):
                result = _find_first_error(messages)
                if result:
                    return result
    return None
