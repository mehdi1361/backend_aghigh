from rest_framework import routers
from rest_framework.response import Response


class BaseApiTitleView(routers.APIRootView):
    """
    This appears where the docstring goes!
    """

    def get(self, request, *args, **kwargs):
        return Response({
            "detail": "Authentication credentials were not provided."
        })


class DefaultRouter(routers.DefaultRouter):
    APIRootView = BaseApiTitleView


api_v1_router = DefaultRouter()
api_v2_router = DefaultRouter()
