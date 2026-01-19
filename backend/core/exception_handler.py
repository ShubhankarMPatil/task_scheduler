from __future__ import annotations

import logging

from django.db import OperationalError, ProgrammingError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """Ensure API endpoints always return JSON (even for unexpected server errors).

    Key production issue: DB migrations not applied can raise ProgrammingError/
    OperationalError (e.g., missing table/column). Those should not return an HTML
    500 page.
    """

    # Let DRF handle standard exceptions first.
    response = exception_handler(exc, context)
    if response is not None:
        return response

    view = context.get("view")
    request = context.get("request")

    # Common production failure: missing migrations / missing relation.
    if isinstance(exc, (ProgrammingError, OperationalError)):
        logger.exception(
            "Database error (likely missing migrations)",
            extra={
                "path": getattr(request, "path", None),
                "view": getattr(view, "__class__", type(view)).__name__ if view else None,
            },
        )
        return Response(
            {
                "detail": "Database is not ready (did you run migrations?).",
                "error": str(exc),
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # Keep 404s as JSON (in case they bubble up as Django Http404)
    if isinstance(exc, Http404):
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    # Fall back to a generic JSON 500.
    logger.exception(
        "Unhandled exception",
        extra={
            "path": getattr(request, "path", None),
            "view": getattr(view, "__class__", type(view)).__name__ if view else None,
        },
    )

    if isinstance(exc, APIException):
        # APIException subclasses already have a status_code; but DRF handler
        # returned None for some reason. Preserve status.
        return Response({"detail": str(exc)}, status=getattr(exc, "status_code", 500))

    return Response(
        {"detail": "Internal server error."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
