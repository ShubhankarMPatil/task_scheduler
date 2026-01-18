from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services import dashboard_metrics


@api_view(["GET"])
def dashboard_view(request):
    user = request.user if request.user.is_authenticated else None
    return Response(dashboard_metrics(user=user))
