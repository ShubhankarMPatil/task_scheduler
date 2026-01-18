from requests import RequestException
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .world_time import fetch_current_time


@api_view(["GET"])
def world_time(_request):
    try:
        data = fetch_current_time()
    except RequestException as exc:
        return Response(
            {"detail": "Failed to fetch world time.", "error": str(exc)},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    # Return a small, stable subset for the UI.
    return Response(
        {
            "timezone": data.get("timezone"),
            "datetime": data.get("datetime"),
            "utc_offset": data.get("utc_offset"),
        }
    )
