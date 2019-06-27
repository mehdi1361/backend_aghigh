from cerberus import Validator
from django.core.cache import cache
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from dashboard.logger import logger_api
from apps.common.viewsets import BaseViewSet
from apps.notification.serializer import NotificationSerializer, FcmTokenUserSerializer
from apps.notification.models import Notification, FcmTokenUser
from apps.notification.schema import add_token_schema
from dashboard.settings.base import CACHE_TIME_ANN_COUNT, CACHE_TIME_NOTIF_COUNT


class NotificationViewSet(BaseViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(send_to_id=request.user.id, seen=False).order_by('-created_date')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(url_path='read', methods=['post'])
    def notify_check(self, request, pk=None):
        Notification.objects.filter(id=pk, send_to_id=request.user.id).update(seen=True)
        calculate_notification_count_set_cache(request.user.id)
        return Response(status=status.HTTP_200_OK)


def calculate_notification_count_set_cache(user_id):
    try:
        cache_key = 'notification_count_{0}'.format(user_id)
        count = Notification.objects.filter(send_to_id=user_id, seen=False).count()
        data = {"count": count}
        # logger_api.error("notification_count  calculate", extra={"detail": {"user": user_id, }})
        cache.set(cache_key, data, CACHE_TIME_NOTIF_COUNT)
    except Exception as ex:
        logger_api.error("calculate_notification_count_set_cache  Error", extra={"detail": {"error": ex, }})


class NotificationCountViewSet(BaseViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    # @method_decorator(cache_page(60))
    def list(self, request, *args, **kwargs):
        cache_key = 'notification_count_{0}'.format(request.user.id)
        data = cache.get(cache_key)
        if data:
            # data = {"count": data['count']}
            # logger_api.info("notification_count  memcache", extra={"detail": {"user": request.user.id, }})
            return Response(data, status=status.HTTP_200_OK)

        count = self.queryset.filter(send_to_id=request.user.id, seen=False).count()
        data = {"count": count}
        cache.set(cache_key, data, CACHE_TIME_NOTIF_COUNT)
        # logger_api.error("notification_count  calculate", extra={"detail": {"user": request.user.id, }})
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        pass

    def retrieve(self, request, *args, **kwargs):
        pass


class FcmTokenUserViewSet(BaseViewSet):
    queryset = FcmTokenUser.objects.all()
    serializer_class = FcmTokenUserSerializer

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        data = request.data
        v = Validator(add_token_schema())
        if v.validate(data):
            device = "web_token" if data["device"] == "web" else "mobile_token"
            token = data["token"]
            query = {device: token}
            fcm_token = self.get_queryset().filter(user_id=request.user.id)
            if fcm_token:
                fcm_token.update(**query)
                return Response(status=status.HTTP_200_OK)

            else:
                query["user_id"] = request.user.id
                FcmTokenUser.objects.create(**query)

                return Response(status=status.HTTP_201_CREATED)
        else:
            # logger_backend.error("Activity change_status_fields_check Error", extra={
            #     "detail": {
            #         "error": v.errors,
            #     }
            # })
            raise ValidationError(v.errors, code=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        pass

    def retrieve(self, request, *args, **kwargs):
        pass
