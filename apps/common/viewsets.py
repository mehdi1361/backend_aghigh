import json
import datetime
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.renderers import AdminRenderer, JSONRenderer, BrowsableAPIRenderer
from rest_framework.pagination import PageNumberPagination
from apps.common.rest_framework_tracking import LoggingMixin
from rest_framework import mixins
from apps.common.models import ApkRelease
from apps.common.serializers import ApkReleaseSerializer

from apps.common.view import make_json_disable_manager
from dashboard.logger import logger_api, logger_api
from dashboard.settings.base import CACHE_TIME_APK_RELEASE


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000


class BaseViewSet(LoggingMixin, viewsets.ModelViewSet):
    def __init__(self, *args, **kwargs):
        super(BaseViewSet, self).__init__(**kwargs)

    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, AdminRenderer,)


class BaseViewSetReadOnly(LoggingMixin, ReadOnlyModelViewSet):
    def __init__(self, *args, **kwargs):
        super(BaseViewSetReadOnly, self).__init__(**kwargs)

    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, AdminRenderer,)


def set_cache_apk_release_student():
    """تابعی که آخرین برنامه موبایل دانش آموز بارگذاری شده روی سرور را در کش ذخیره می کند """
    # kahrizi
    cache_key = 'apk_release_student'
    queryset = ApkRelease.objects.filter(type="student").order_by('-created_at')[0]
    serializer = ApkReleaseSerializer(queryset)
    cache.set(cache_key, serializer.data, CACHE_TIME_APK_RELEASE)
    # logger_api.error("apk_release_teacher calculate", extra={})


def set_cache_apk_release_teacher():
    """تابعی که آخرین برنامه موبایل مربی بارگذاری شده روی سرور را در کش ذخیره می کند """
    # kahrizi
    cache_key = 'apk_release_teacher'
    queryset = ApkRelease.objects.filter(type="teacher").order_by('-created_at')[0]
    serializer = ApkReleaseSerializer(queryset)
    cache.set(cache_key, serializer.data, CACHE_TIME_APK_RELEASE)
    # logger_api.error("apk_release_teacher calculate", extra={})


def set_cache_apk_release_hamraz():
    """تابعی که آخرین برنامه موبایل مربی بارگذاری شده روی سرور را در کش ذخیره می کند """
    # kahrizi
    cache_key = 'apk_release_hamraz'
    queryset = ApkRelease.objects.filter(type="hamraz").order_by('-created_at')[0]
    serializer = ApkReleaseSerializer(queryset)
    cache.set(cache_key, serializer.data, CACHE_TIME_APK_RELEASE)
    # logger_api.error("apk_release_hamraz calculate", extra={ })


class ApkReleaseViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = ApkRelease.objects.all()
    serializer_class = ApkReleaseSerializer

    authentication_classes = (())
    permission_classes = (())
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, AdminRenderer,)

    def list(self, request, *args, **kwargs):
        """
          this function expire in new version of server
        :param request:
        :return: application address
        """
        queryset = self.queryset.filter(type="student").order_by('-created_at')[0]
        serializer = self.get_serializer(queryset, many=False)
        return Response(serializer.data)

    @list_route(url_path='student', methods=['get'])
    def student(self, request):
        """
          last app from student
        :param request:
        :return: application address
        """
        try:
            cache_key = 'apk_release_student'
            data = cache.get(cache_key)
            if data:
                # logger_api.info("apk_release_student  memcache", extra={})
                return Response(data)
        except Exception as e:
            logger_api.error("apk_release_student  get cache  Error", extra={
                "detail": {
                    "error": e,
                }
            })

        queryset = self.queryset.filter(type="student").order_by('-created_at')[0]
        serializer = self.get_serializer(queryset, many=False)
        # logger_api.error("apk_release_student calculate", extra={})
        cache.set(cache_key, serializer.data, CACHE_TIME_APK_RELEASE)  # ست کردن کش
        return Response(serializer.data)

    @list_route(url_path='teacher', methods=['get'])
    def teacher(self, request):
        """
          last app from teacher
        :param request:
        :return: application address
        """
        try:
            cache_key = 'apk_release_teacher'
            data = cache.get(cache_key)
            if data:
                # logger_api.info("apk_release_teacher  memcache", extra={})
                return Response(data)
        except Exception as e:
            logger_api.error("apk_release_teacher  get cache  Error", extra={
                "detail": {
                    "error": e,
                }
            })

        queryset = self.queryset.filter(type="teacher").order_by('-created_at')[0]
        serializer = self.get_serializer(queryset, many=False)
        # logger_api.error("apk_release_teacher calculate", extra={})

        cache.set(cache_key, serializer.data, CACHE_TIME_APK_RELEASE)  # ست کردن کش
        return Response(serializer.data)

    @list_route(url_path='hamraz', methods=['get'])
    def hamraz(self, request):
        """
          last app from hamraz
        :param request:
        :return: application address
        """
        try:
            cache_key = 'apk_release_hamraz'
            data = cache.get(cache_key)
            if data:
                # logger_api.info("apk_release_hamraz  memcache", extra={})
                return Response(data)
        except Exception as e:
            cache_key = 'apk_release_hamraz'
            logger_api.error("apk_release_hamraz  get cache  Error", extra={
                "detail": {
                    "error": e,
                }
            })
        queryset = self.queryset.filter(type="hamraz").order_by('-created_at')
        if queryset:
            queryset = queryset[0]
        serializer = self.get_serializer(queryset, many=False)
        # logger_api.error("apk_release_hamraz calculate", extra={})
        cache.set(cache_key, serializer.data, CACHE_TIME_APK_RELEASE)  # ست کردن کش
        return Response(serializer.data)


class DisablePartViewSet(BaseViewSet):
    # last_date_make_json = datetime.datetime.now()  # تاریخ ساخت جیسون

    def list(self, request, *args, **kwargs):
        """
        برگرداندن جیسون بخش های غیرفعال سامانه
        """
        try:
            # now = datetime.datetime.now()
            # day_len = datetime.timedelta(days=1)# datetime.timedelta(days=1)#86400

            # json_file_disable_manager = Path(settings.BASE_DIR + '/static/DisableManager.json')
            json_file_disable_manager = Path(settings.BASE_DIR + '/static/DisableManager.json')
            if not json_file_disable_manager.is_file():  # اگر فایل جیسون وجود نداشت ساخته شود
                make_json_disable_manager()
                DisablePartViewSet.last_date_make_json = datetime.datetime.now()

            # if (now-DisablePartViewSet.last_date_make_json) >= day_len:# اگر یک روز از ساخت جیسون گذشته بود مجددا ساخته شود چون ممکن است بر اساس تاریخ یک بخش غیرفعال شود
            #     make_json_disable_manager()
            #     DisablePartViewSet.last_date_make_json = datetime.datetime.now()

            # TODO بجای اینکه هر بار از جیسون بخش های غیرفعال خوانده شود در رم نگه داریم و هر بار که تغییر کرد آن را بروز کنیم
            with open(settings.BASE_DIR + '/static/DisableManager.json', encoding='utf-8') as data_file:
                data = json.loads(data_file.read())
                return Response(data)

        except Exception:
            return Response([])
