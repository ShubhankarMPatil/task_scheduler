from datetime import date

from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services import dashboard_metrics


def _parse_date_param(value: str | None) -> date:
    if not value:
        return timezone.localdate()
    try:
        return date.fromisoformat(value)
    except ValueError:
        return timezone.localdate()


@api_view(["GET"])
def dashboard_view(request):
    user = request.user if request.user.is_authenticated else None
    selected_date = _parse_date_param(request.query_params.get("date"))
    return Response(dashboard_metrics(user=user, date=selected_date))
