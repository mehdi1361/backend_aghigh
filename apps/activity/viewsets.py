import json
import copy
import datetime
import threading

import shutil
from django.db.models import Q, Avg, Sum, Count
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import detail_route, list_route
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from cerberus import Validator
from django.conf import settings
from apps.activity.static import GENDER
from apps.league.serializer import SchoolSerializer
from apps.user.models import Student
from dashboard.logger import logger_v1
from handlers.ip_helpers import get_client_ip
from django.core.files.storage import FileSystemStorage
from utils.user_type import get_user_type, get_user_level, get_user_location, has_perm_both_gender
from apps.league.models import Province, School
from apps.common.viewsets import BaseViewSet, BaseViewSetReadOnly
from apps.emtiaz.models import SumActivityParam, Param, ParamActivityComment
from apps.emtiaz.tasks import computing_point_activity
from apps.common.viewsets import LargeResultsSetPagination
from apps.activity.schema import additional_fields_add_schema, field_change_status_schema
from apps.notification.tasks import send_notification_student_activity, send_notification_teacher_activity
from apps.emtiaz.static import POINT_EMTIAZ
from apps.common.some_script import Script
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import os
from apps.common.app_enable import app_enable
from apps.common.utils import PartProject
from apps.activity.messages import (
    ERROR_IMAGE_COUNT,
    ADDITIONAL_FIELD_INCORRECT,
    REQUIRED_FIELD_NULL,
    CHANGE_CATEGORY_STATUS,
    START_DATE_LESS_THAN_END_DATE,
    ERROR_FILE_COUNT, ERROR_FILE_TYPE, ERROR_FILE_SIZE)
from apps.activity.serializers import (
    ActivityCategorySerializer,
    CreateActivitySerializer,
    ActivitySerializer,
    BoxActivitySerializer,
    GroupAdditionalFieldsSerializer,
    BoxActivityWorkspaceCoachSerializer,
    BoxActivityWorkspaceOtherLevelSerializer,
    AdditionalFieldSerializer,
    BoxActivityHistoryCoachSerializer,
    RateUsersActivitySerializer,
    CategoriesReportSerializer,
    ReportAbuseSerializer,
    BoxReportAbuseSerializer,
    ActivityMainSerializer,
    ReportAbuseGroupSerializer
)
from apps.activity.models import (
    ImageActivity,
    FileActivity,
    ActivityAdditionalFields,
    Activity,
    ActivityCategory,
    AdditionalField,
    GroupAdditionalFields,
    ActivityDailyReport,
    RateActivity,
    ActivityLike,
    StudentDailyReport,
    CategoriesReport,
    ReportAbuse,
    ActivityState,
    DropDownFormSomeAdditionalField)


class CategoriesReportViewSet(BaseViewSet):
    queryset = CategoriesReport.objects.all()
    serializer_class = CategoriesReportSerializer


class ReportAbusesViewSet(BaseViewSet):
    queryset = ReportAbuse.objects.all()
    serializer_class = ReportAbuseSerializer

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        queryset = self.queryset.filter(
            activity_id=pk
        )
        if queryset:
            data = {
                'activity_title': queryset[0].activity.title,
                'activity_id': queryset[0].activity_id,
                'reports': BoxReportAbuseSerializer(queryset, many=True).data
            }
            return Response(data=data, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        data = copy.copy(request.data)
        data['sender'] = request.user.id
        self.perform_create_or_update(data)
        return Response(data, status=status.HTTP_201_CREATED)

    @staticmethod
    def perform_create_or_update(data):
        ReportAbuse.objects.update_or_create(
            activity_id=data['activity'],
            sender_id=data['sender'],
            defaults={
                'activity_id': data['activity'],
                'sender_id': data['sender'],
                'content': data.get('content', ""),
                'category_id': data['category']
            },
        )

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.exclude(activity__state="BAN").values('activity_id', 'activity__school__name', 'activity__school_id', 'activity__title').annotate(count=Count('id')).order_by('-count')

        self.serializer_class = ReportAbuseGroupSerializer
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ActivityViewSet(BaseViewSet):
    queryset = Activity.objects.all()
    serializer_class = BoxActivitySerializer

    @detail_route(url_path='rate', methods=['post'])
    @app_enable(PartProject.activity_star)
    def rate_activity(self, request, pk=None):
        data = request.data
        user_id = request.user.id
        rate = int(data["rate"])
        user_type = get_user_type(request.user)
        if user_type == 'student':
            activity = Activity.objects.filter(id=pk)
            if activity.exists() and user_id != activity.get().student_id:

                rates = RateActivity.objects.filter(
                    activity_id=pk
                )

                rate_activity = rates.filter(student_id=user_id)

                average_absolute = self.get_average_absolute(rate, user_id, pk)

                if rate_activity.exists():
                    rate_activity = rate_activity.get()
                    rate_activity.rate = rate
                    rate_activity.average_absolute = average_absolute
                    rate_activity.save()

                else:
                    thread_worker = threading.Thread(target=self.create_rate_activity, args=(
                        activity, average_absolute, pk, rate, rates, request, user_id
                    ))
                    thread_worker.start()

                    thread_worker = threading.Thread(target=self.daily_student_point_change,
                                                     args=(request.user.baseuser.student.id,))
                    thread_worker.start()

                if rates:
                    aggregate = rates.aggregate(Avg('rate'), Sum('average_absolute'))
                else:
                    aggregate = {
                        "rate__avg": rate,
                        "average_absolute__sum": rate
                    }

                activity.update(
                    point_emtiaz=aggregate["rate__avg"],
                    point_emtiaz_sum=aggregate["average_absolute__sum"],
                    rate_count=rates.count()
                )

                _dict_rate = {
                    "count": rates.count(),
                    "average": float("{0:.2f}".format(activity.get().point_emtiaz)),
                    "user_rate": rate
                }

                thread_worker = threading.Thread(target=self.daily_activity_point_change, args=(pk, rates))
                thread_worker.start()

                return Response(
                    status=status.HTTP_200_OK,
                    data=_dict_rate
                )
            else:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            return Response(
                {"message": "morabi hasti"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @detail_route(url_path='change_state', methods=['post'])
    def change_state_activity(self, request, pk=None):
        if "country" not in get_user_level(request.user):
            return Response(
                status=status.HTTP_403_FORBIDDEN,
            )

        state_activity = request.data.get("state", '')
        if state_activity not in ['BAN']:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
            )

        Activity.objects.filter(id=pk).update(state=state_activity)

        return Response(
            status=status.HTTP_200_OK,
        )

    def create_rate_activity(self, activity, average_absolute, pk, rate, rates, request, user_id):
        count_rates = rates.count()
        rate_model = RateActivity()
        rate_model.activity_id = int(pk)
        rate_model.student_id = int(user_id)
        rate_model.rate = rate
        rate_model.average_absolute = average_absolute
        if count_rates == 0:
            rate_model.first_like = True

        rate_model.point_student = self.get_point_student_from_emtiaz_activity(
            student_school=request.user.baseuser.student.school,
            activity=activity.get(),
            rates_count=count_rates,
        )
        rate_model.save()

    @detail_route(url_path='rate_users', methods=['get'])
    @app_enable(PartProject.activity_rate_users)
    def rate_users(self, request, pk=None):

        activity = Activity.objects.filter(id=pk)
        if activity.exists():

            # get all users that rate to this activity
            queryset = RateActivity.objects.filter(activity_id=pk).select_related("student")

            self.serializer_class = RateUsersActivitySerializer
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(
                status=status.HTTP_200_OK,
                data=serializer.data
            )
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
            )

    @staticmethod
    def daily_activity_point_change(activity_id, rates):
        today = datetime.datetime.today()
        today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)

        daily_report = ActivityDailyReport.objects.filter(activity_id=int(activity_id), date=today)
        aggregate = rates.filter(
            updated_at__range=(today_min, today_max)
        ).aggregate(Sum('average_absolute'))["average_absolute__sum"]

        average_absolute = aggregate if aggregate is not None else 0

        thread_worker = threading.Thread(target=Script().activity_emtiaz(), args=(activity_id,))
        thread_worker.start()

        if daily_report.exists():
            daily_report.update(point=average_absolute)

        else:
            ActivityDailyReport(
                date=today,
                point=average_absolute,
                activity_id=int(activity_id)
            ).save()

    @staticmethod
    def get_average_absolute(rate, user_id, activity_id):
        student_comment = ParamActivityComment.objects.filter(
            ~Q(value=0),
            activity_comment__sender_id=user_id,
            activity_comment__activity_id=activity_id,
        ).aggregate(Avg('value'))['value__avg']

        if student_comment and student_comment != 0:
            average_absolute = (student_comment + rate) / 2

        else:
            average_absolute = rate
        return int(average_absolute)

    @detail_route(url_path='check', methods=['post'])
    @app_enable(PartProject.activity_check)
    def activity_check(self, request, pk=None):
        user_type = get_user_type(request.user)
        if user_type != 'student':
            activity = self.queryset.filter(
                id=pk,
            )
            if activity:
                activity_id = activity.get().id
                try:
                    data = json.loads(request.data['data'])
                except Exception as e:
                    logger_v1.error("Activity activity_check Error", extra={
                        "detail": {
                            "error": e,
                        }
                    })
                    return Response(status=status.HTTP_400_BAD_REQUEST)

                with transaction.atomic():
                    general_status = self.action_change_activity_general_field(activity, data)
                    field_status = self.action_change_activity_field(activity_id, data, general_status)

                    if general_status and field_status:
                        activity.update(state='ACCEPT', accepted_at=datetime.datetime.now(),
                                        updated_at=datetime.datetime.now())
                    else:
                        activity.update(state='SHE', updated_at=datetime.datetime.now(), reject_count=activity.get().reject_count + 1)

                activity.update(checker=request.user.id)
                send_notification = threading.Thread(target=send_notification_student_activity, args=(activity.get(),))
                send_notification.start()

                try:
                    if general_status and field_status:
                        computing_point = threading.Thread(target=computing_point_activity, args=(activity_id,))
                        computing_point.start()

                except Exception as e:
                    logger_v1.error("Activity api computing_point_activity Error", extra={
                        "detail": {
                            "error": e,
                        }
                    })

                serializer = self.get_serializer(activity.get(), many=False)
                return Response(serializer.data)

        return Response(status=status.HTTP_403_FORBIDDEN)

    @detail_route(url_path='confirm', methods=['post'])
    @app_enable(PartProject.activity_check)
    def activity_confirm(self, request, pk=None):
        user_type = get_user_type(request.user)
        if user_type != 'student':
            activity = self.queryset.filter(
                id=pk,
            )
            if activity:
                self.confirm_activity(activity.get(), request.user.id)

                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_403_FORBIDDEN)

    @detail_route(url_path='update', methods=['post'])
    @app_enable(PartProject.activity_update)
    def update_activity(self, request, pk=None):
        data = copy.copy(request.data)
        _activity = self.queryset.filter(
            id=pk,
            student_id=request.user.id
        )
        if _activity.exists():
            with transaction.atomic():
                activity = _activity.get()
                self.check_general_data_valid(data, activity)
                self.check_valid_image_length(data=data, action='updated', activity=activity)
                self.check_valid_additional_files(data=data, action='updated', activity=activity)
                self.update_images(data, activity)
                self.update_files(data, activity)
                self.update_additional_field(data, _activity)
                self.update_general_field(data, _activity)
                self.update_files_additional_fields(activity=activity, data=data)

                bool_activity = self.check_for_accept_activity(activity)
                if bool_activity:
                    _activity.update(state="ACCEPT", accepted_at=datetime.datetime.now(),
                                     updated_at=datetime.datetime.now())
                else:
                    _activity.update(state="SHR", updated_at=datetime.datetime.now())

            try:
                send_notification = threading.Thread(target=send_notification_teacher_activity, args=(_activity.get(),))
                send_notification.start()

            except Exception as e:
                logger_v1.error("send_notification_teacher_activity Error", extra={
                    "detail": {
                        "error": e,
                    }
                })

            try:
                if bool_activity:
                    computing_point = threading.Thread(target=computing_point_activity, args=(activity.id,))
                    computing_point.start()

            except Exception as e:
                logger_v1.error("Activity api computing_point_activity Error", extra={
                    "detail": {
                        "error": e,
                    }
                })

            serializer = self.get_serializer(activity, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def check_general_data_valid(data, activity):
        start_date = False
        end_date = False
        list_general_field = ["title", "location", "description"]
        now = datetime.datetime.now()

        if "end_date" in data:
            try:
                end_date = datetime.datetime.strptime(data["end_date"], '%Y-%m-%dT%H:%M')
            except:
                try:
                    end_date = datetime.datetime.strptime(data["end_date"], '%Y-%m-%dT%H:%M:%S')
                except:
                    raise ValidationError({"end_date": START_DATE_LESS_THAN_END_DATE}, code=status.HTTP_400_BAD_REQUEST)

        if "start_date" in data:
            try:
                start_date = datetime.datetime.strptime(data["start_date"], '%Y-%m-%dT%H:%M')
            except:
                try:
                    start_date = datetime.datetime.strptime(data["start_date"], '%Y-%m-%dT%H:%M:%S')
                except:
                    raise ValidationError({"start_date": START_DATE_LESS_THAN_END_DATE},
                                          code=status.HTTP_400_BAD_REQUEST)

        if start_date and activity.end_date_status:
            if start_date > activity.end_date:
                raise ValidationError({"start_date_lower": START_DATE_LESS_THAN_END_DATE},
                                      code=status.HTTP_400_BAD_REQUEST)

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError({"start_date_lower": START_DATE_LESS_THAN_END_DATE},
                                      code=status.HTTP_400_BAD_REQUEST)

        if not activity.start_date_status and not activity.end_date_status:
            if start_date > now or end_date > now:
                raise ValidationError({"date_future": ""}, code=status.HTTP_400_BAD_REQUEST)

        if end_date and activity.start_date_status:
            if end_date < activity.start_date:
                raise ValidationError({"start_date_lower": START_DATE_LESS_THAN_END_DATE},
                                      code=status.HTTP_400_BAD_REQUEST)

        for field in list_general_field:
            if field in data and data[field] == "":
                raise ValidationError({field: str(field) + " not valid"}, code=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def remove_old_additional_field(activity):
        all_fields = ActivityAdditionalFields.objects.filter(activity_id=activity.id)
        additional_fields = all_fields.filter(additional_field__field_type="file_upload")
        if additional_fields:
            # remove files that upload for old additional fields this activity
            ActivityViewSet.delete_files_additional_from_path(activity, additional_fields)

        if all_fields:
            all_fields.delete()

    @staticmethod
    def delete_files_additional_from_path(activity, additional_fields):
        for additional_field in additional_fields:
            additional_field_name = json.loads(additional_field.value)['title']
            additional_field_id = additional_field.additional_field.id

            # file path that previous saved file
            file_path = "{0}/additional_fields_files/{1}/{2}/{3}".format(settings.MEDIA_ROOT, activity.id, additional_field_id, additional_field_name)
            if os.path.exists(file_path):
                # delete files from directory
                os.remove(file_path)

    @staticmethod
    def update_general_field(data, _activity):
        update_data = {}
        activity = _activity.get()
        if not activity.title_status and 'title' in data:
            update_data['title'] = data['title']

        if not activity.location_status and 'location' in data:
            update_data['location'] = data['location']

        if not activity.start_date_status and 'start_date' in data:
            update_data['start_date'] = data['start_date']

        if not activity.end_date_status and 'end_date' in data:
            update_data['end_date'] = data['end_date']

        if not activity.description_status and 'description' in data:
            update_data['description'] = data['description']

        _activity.update(**update_data)

    @staticmethod
    def get_status_activity(activity):
        activity = activity.get()
        if activity.title_status and activity.location_status and \
                activity.start_date_status and activity.end_date_status \
                and activity.category_status and activity.description_status:
            return True
        return False

    @staticmethod
    def get_params(request):
        query_params = request.query_params.copy()
        dict_params = {}
        list_param_int = [
            'vip', 'school', 'point_start', 'point_end',
            'province', 'county', 'my_school',
            'most_view', 'random', 'history', 'category', 'department'
        ]
        list_param_str = ['text', 'view', 'role', 'gender', 'order']
        for key, value in query_params.items():
            if key in list_param_int:
                if query_params[key].isdigit():
                    dict_params[key] = int(value)
                    continue
            if key in list_param_str:
                dict_params[key] = str(value)
        return dict_params

    def get_query(self, user, dict_params):
        user_type = get_user_type(user)
        orders = []
        exclude = {}
        _random = False
        q_object = Q()

        if user_type == "teacher":
            has_perm = has_perm_both_gender(self.request.user)
            if has_perm:
                gender = GENDER.get(self.request.query_params.get('gender', self.request.user.baseuser.gender), self.request.user.baseuser.gender)
            else:
                gender = self.request.user.baseuser.gender

            q_object.add(Q(gender=gender), Q.AND)

            if 'history' not in dict_params:
                orders.append('updated_at')
                levels = get_user_level(user, 'teacher')
                role = dict_params.get('role', 'coach')
                if not levels or role not in levels:
                    raise ValidationError({"message": "user no has permission"}, code=status.HTTP_400_BAD_REQUEST)

                q_coach = False
                if role == "coach":
                    self.serializer_class = BoxActivityWorkspaceCoachSerializer
                    q_object.add(Q(school__teacher_id=user.id), Q.AND)
                    q_object.add(Q(state__in=['NEW', 'SHR']), Q.AND)
                    q_coach = True

                elif role == "camp":
                    q_object.add(Q(school__camp__coach_id=user.id), Q.AND)

                elif role == "county":
                    q_object.add(Q(school__county__coach_id=user.id), Q.AND)

                elif role == "province" or role == "province_m" or role == "province_f":
                    provinces = Province.objects.filter(coaches__id=user.id)
                    _provinces = []
                    for province in provinces:
                        _provinces.append(province.id)

                    q_object.add(Q(school__province__in=_provinces), Q.AND)

                if not q_coach:
                    self.serializer_class = BoxActivityWorkspaceOtherLevelSerializer
                    time_threshold = datetime.datetime.now() - datetime.timedelta(days=3)
                    q_object.add(Q(updated_at__lt=time_threshold), Q.AND)
                    q_object.add(Q(state__in=['NEW', 'TIL', 'SHR']), Q.AND)
            else:
                self.serializer_class = BoxActivityHistoryCoachSerializer
                q_object.add(Q(checker_id=user.id), Q.AND)
                q_object.add(Q(state__in=['ACCEPT', 'SHR', 'SHE', 'BAN']), Q.AND)
        else:
            q_object.add(Q(school_id=user.baseuser.student.school.id), Q.AND)
            q_object.add(~Q(state='BAN'), Q.AND)

        return q_object, exclude, orders, _random

    @staticmethod
    def get_order(camp_id, county_id, province_id, dict_params, orders, q_object):
        if dict_params["order"] == "newest" or dict_params['order'] == '1':
            orders.append('-accepted_at')

        elif dict_params["order"] == "most_view":
            orders.append('-view_count')

        elif dict_params["order"] == "newest_province":
            q_object.add(Q(school__province_id=province_id), Q.AND)
            orders.append('-accepted_at')

        elif dict_params["order"] == "newest_county":
            q_object.add(Q(school__county_id=county_id), Q.AND)
            orders.append('-accepted_at')

        elif dict_params["order"] == "newest_camp":
            q_object.add(Q(school__camp_id=camp_id), Q.AND)
            orders.append('-accepted_at')

        elif dict_params["order"] == "point_high":
            orders.append('-point_emtiaz_sum')

        elif dict_params["order"] == "point_low":
            orders.append('point_emtiaz_sum')

        elif dict_params["order"] == "zero_point":
            q_object.add(Q(point_emtiaz__lte=0), Q.AND)
            orders.append('accepted_at')

        elif dict_params["order"] == "trend":
            q_object.add(Q(comments_count__gte=1), Q.AND)
            orders.append('-comments_count')

        else:
            orders.append('accepted_at')

    @staticmethod
    def check_valid_image_length(data, action='created', activity=None):
        count_images = len(data.getlist('images[]', []))
        if action == 'created':
            if count_images < 3:
                logger_v1.error("Activity check_valid_image_length Error", extra={
                    "detail": {
                        "error": ERROR_IMAGE_COUNT,
                    }
                })
                raise ValidationError({"images": ERROR_IMAGE_COUNT}, code=status.HTTP_400_BAD_REQUEST)

        else:
            activity_image = ImageActivity.objects.filter(
                activity_id=activity.id,
                archive=False
            ).count()
            try:
                count_deleted_images = len(json.loads(data.get('deleted_images', '[]')))
            except Exception as e:
                logger_v1.error("Activity check_valid_image_length Error", extra={
                    "detail": {
                        "error": e,
                    }
                })
                raise ValidationError(e, code=status.HTTP_400_BAD_REQUEST)

            if count_images + activity_image - count_deleted_images < 3:
                logger_v1.error("Activity check_valid_image_length Error", extra={
                    "detail": {
                        "error": ERROR_IMAGE_COUNT,
                    }
                })
                raise ValidationError({"images": ERROR_IMAGE_COUNT}, code=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def check_valid_additional_files(data, action='created', activity=None):
        # select files for delete
        deleted_files = json.loads(data.get('deleted_additional_files', '[]'))
        # action update and select files for delete
        if action == "updated" and deleted_files:
            for activity_additional_id in deleted_files:
                # additional_fields_info = ActivityAdditionalFields.objects.filter(
                #     activity=activity
                # ).annotate(Count('additional_field')).values('additional_field__count', 'additional_field_id', 'additional_field__validate_data').filter(id=activity_additional_id)
                additional_fields_info = ActivityAdditionalFields.objects.filter(activity=activity, id=activity_additional_id)[0].additional_field

                # Todo correct this code later
                additional_field_id = additional_fields_info.id
                validator = additional_fields_info.validate_data

                key = "additional_fields_files_{0}_[]".format(additional_field_id)
                all_upload_files = len(data.getlist(key, []))
                deleted_files_count = 0
                files_all_list = ActivityAdditionalFields.objects.filter(additional_field_id=additional_field_id, activity=activity).values_list("id", flat=True)
                saved_files_count = len(files_all_list)
                for item in files_all_list:
                    if item in deleted_files:
                        deleted_files_count += 1

                files_count = all_upload_files + saved_files_count - deleted_files_count

                if validator['min_file_count'] != -1 or validator['max_file_count'] != -1:
                    # check file count
                    if not (validator['min_file_count'] <= files_count <= validator['max_file_count']):
                        raise ValidationError({"additional_files_count": ERROR_FILE_COUNT}, code=status.HTTP_400_BAD_REQUEST)

        for key in data.keys():
            # get keys that start with additional_fields_files_
            if key.startswith("additional_fields_files_"):
                # get id additional_fields
                additional_field_id = str(key).split("_")[-2]
                validator = AdditionalField.objects.filter(id=int(additional_field_id))[0].validate_data
                # get all upload files for one additional_fields
                all_upload_files = data.getlist(key, [])
                if action == "created":
                    # additional field required check count
                    if validator['min_file_count'] != -1 or validator['max_file_count'] != -1:
                        # check file count
                        if not (validator['min_file_count'] <= len(all_upload_files) <= validator['max_file_count']):
                            raise ValidationError({"additional_files_count": ERROR_FILE_COUNT}, code=status.HTTP_400_BAD_REQUEST)

                formats_list = validator['format']
                max_file_size = validator['max_file_size']
                min_file_size = validator['min_file_size']

                for my_file in all_upload_files:

                    # additional field required check file format
                    if formats_list:
                        # get file type and convert to lower char
                        file_type = my_file.name.split('.')[-1].lower()
                        if file_type not in formats_list:
                            raise ValidationError({"additional_files_type": ERROR_FILE_TYPE}, code=status.HTTP_400_BAD_REQUEST)

                    # additional field required check size
                    if min_file_size != -1 or max_file_size != -1:
                        file_size = my_file.size / 1024
                        # check file size
                        if not (min_file_size <= file_size <= max_file_size):
                            raise ValidationError({"additional_files_size": ERROR_FILE_SIZE}, code=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def save_image(images, activity):
        for img in images:
            image_model = ImageActivity()
            image_model.image = img
            image_model.activity = activity
            image_model.save()

    @staticmethod
    def save_file(files, activity):
        for file in files:
            file_model = FileActivity()
            file_model.file = file
            file_model.activity = activity
            file_model.save()

    @staticmethod
    def save_additional_field(additional_fields, activity, category_id=None):
        if category_id:
            fields = list(AdditionalField.objects.filter(~Q(func_name="func3"), category=category_id))
        else:
            fields = list(AdditionalField.objects.filter(~Q(func_name="func3"), category=activity.category_id))

        _dict_fields = {}
        if len(fields) == 0:
            return
        # Todo after delete comment and review process for check
        # if len(fields) != len(additional_fields):
        #     logger_v1.error("Activity save_additional_field Error", extra={
        #         "detail": {
        #             "error": ADDITIONAL_FIELD_INCORRECT,
        #         }
        #     })
        #     raise ValidationError({"additional_fields": ADDITIONAL_FIELD_INCORRECT}, code=status.HTTP_400_BAD_REQUEST)

        for field in fields:
            _dict_fields[field.id] = field.required

        v = Validator(additional_fields_add_schema())
        for r_field in additional_fields:
            if not v.validate(r_field):
                logger_v1.error("Activity save_additional_field Error", extra={
                    "detail": {
                        "error": v.errors,
                    }
                })
                raise ValidationError({"additional_fields": v.errors}, code=status.HTTP_400_BAD_REQUEST)

            if r_field['id'] in _dict_fields and _dict_fields[r_field['id']] and not r_field['value']:
                logger_v1.error("Activity save_additional_field Error", extra={
                    "detail": {
                        "error": REQUIRED_FIELD_NULL,
                    }
                })
                raise ValidationError({"additional_fields": REQUIRED_FIELD_NULL}, code=status.HTTP_400_BAD_REQUEST)

            if r_field['id'] in _dict_fields.keys():
                try:
                    activity_additional = ActivityAdditionalFields()
                    activity_additional.activity = activity
                    activity_additional.additional_field_id = r_field['id']
                    activity_additional.value = r_field['value']
                    activity_additional.save()
                except Exception as ex:
                    raise ValidationError({"additional_fields_too_long": str(ex).strip()}, code=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def save_state(request, activity):

        state_data = dict()

        client_ip = get_client_ip(request)
        state_data["viewer_ip"] = client_ip
        state_data["viewer_id"] = request.user.id
        state_data["activity"] = activity
        try:
            ActivityState(**state_data).save()
            activity.view_count += 1
            activity.save()

            if request.user.baseuser:
                state_data["viewer"] = request.user.baseuser
        except:
            pass

    @staticmethod
    def action_change_activity_general_field(activity, data):
        update_data = {}
        data_activity = activity.get()
        active_bool = True
        if not data_activity.title_status and 'title_status' in data:
            update_data['title_status'] = data['title_status']
            update_data['title_comment'] = data.get('title_comment', '')
            if not data['title_status']:
                active_bool = False

        if not data_activity.location_status and 'location_status' in data:
            update_data['location_status'] = data['location_status']
            update_data['location_comment'] = data.get('location_comment', '')
            if not data['location_status']:
                active_bool = False

        if not data_activity.start_date_status and 'start_date_status' in data:
            update_data['start_date_status'] = data['start_date_status']
            update_data['start_date_comment'] = data.get('start_date_comment', '')
            if not data['start_date_status']:
                active_bool = False

        if not data_activity.end_date_status and 'end_date_status' in data:
            update_data['end_date_status'] = data['end_date_status']
            update_data['end_date_comment'] = data.get('end_date_comment', '')
            if not data['end_date_status']:
                active_bool = False

        if not data_activity.description_status and 'description_status' in data:
            update_data['description_status'] = data['description_status']
            update_data['description_comment'] = data.get('description_comment', '')
            if not data['description_status']:
                active_bool = False

        if not data_activity.category_status and 'category_status' in data:
            update_data['category_status'] = data['category_status']
            update_data['category_comment'] = data.get('category_comment', '')
            if not data['category_status']:
                active_bool = False

        if 'general_comment' in data:
            active_bool = False

        update_data['general_comment'] = data.get('general_comment', '')

        activity.update(**update_data)
        return active_bool

    @staticmethod
    def change_status_fields_check(fields, model_db, activity_id, additional_files=None):
        v = Validator(field_change_status_schema())
        v.allow_unknown = True
        for field in fields:
            if v.validate(field):
                _dict_query = {
                    "activity_id": activity_id,
                }
                if model_db == ActivityAdditionalFields:
                    if additional_files:
                        _dict_query['id'] = field['id']
                    else:
                        _dict_query["additional_field_id"] = field["id"]
                else:
                    _dict_query["id"] = field["id"]

                r_field = model_db.objects.filter(**_dict_query)
                if r_field and not r_field[0].status:
                    r_field.update(status=field['status'], comment=field['comment'])
            else:

                logger_v1.error("Activity change_status_fields_check Error", extra={
                    "detail": {
                        "error": v.errors,
                    }
                })
                raise ValidationError(v.errors, code=status.HTTP_400_BAD_REQUEST)

    @app_enable(PartProject.activity_show)
    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = ActivitySerializer
        pk = int(kwargs.get("pk"))
        activity_year = ActivityReadOnlyViewSet.get_activity_year(
            request.query_params.get('activity_year', 'default')
        )
        try:
            activity = Activity.objects.using(activity_year).get(id=pk)

            if activity.state == "SHE":  # برای نمایش فعالیت رد شده توسط مربی به دانش آموز جدید یک مدرسه
                students = list(Student.objects.filter(school__id=activity.school_id).values_list('id', flat=True))
                if self.request.user.id not in students:
                    return Response(status=status.HTTP_403_FORBIDDEN)
            elif activity.state == "BAN":
                # students = list(Student.objects.filter(school__id=activity.school_id).values_list('id', flat=True))
                # if self.request.user.id not in students and self.request.user.id != activity.checker_id:
                if self.request.user.id != activity.student_id or self.request.user.id != activity.checker_id:
                    return Response(status=status.HTTP_404_NOT_FOUND)

            if activity_year == "default" and activity.state == "ACCEPT":
                self.save_state(request, activity)

            data = self.get_serializer(activity).data
            data["params"] = self.set_params(pk, activity_year)

            return Response(data)

        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def set_params(pk, db_name):
        params = Param.objects.using(db_name).filter()
        average = []
        for param in params:
            _p = SumActivityParam.objects.using(db_name).filter(activity_id=pk, param_id=param.id)
            if _p:
                _p = _p[0]
                res = {
                    "id": param.id,
                    "title": param.title,
                    "value": _p.sum / _p.count
                }
            else:
                res = {
                    "id": param.id,
                    "title": param.title,
                    "value": 0
                }
            average.append(res)
        return average

    def list(self, request, *args, **kwargs):
        params = self.get_params(request)
        query, exclude, orders, _random = self.get_query(request.user, params)
        queryset = self.queryset.filter(query).exclude(**exclude).order_by(*orders)

        if _random:
            queryset = queryset.order_by('?').distinct()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)

            return response

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def save_like(self, request, pk):

        activity = self.queryset.filter(id=pk).get()

        like_data = dict()
        user = None
        if request.user.baseuser:
            user = request.user.baseuser

        client_ip = get_client_ip(request)
        like_data["liker_ip"] = client_ip

        mime_code = None
        if "mime_code" in request.META:
            mime_code = request.META["mime_code"]
            like_data["liker_mime"] = mime_code

        activity_likes = ActivityLike.objects.filter(
            Q(activity=activity, liker=user) |
            Q(activity=activity, liker_ip=client_ip, liker_mime=mime_code)
        )

        if activity_likes.exists():
            activity_likes.delete()

            if activity.like_count > 0:
                activity.like_count = activity.like_count - 1
                activity.save()

            return False, activity.like_count

        activity.like_count = activity.like_count + 1
        activity.save()

        like_data["activity"] = activity
        if request.user.baseuser:
            like_data["liker"] = request.user.baseuser

        ActivityLike(**like_data).save()
        return True, activity.like_count

    def action_change_activity_field(self, activity_id, data, general_status):
        self.change_status_fields_check(data.get('additional_field', []), ActivityAdditionalFields, activity_id)
        self.change_status_fields_check(data.get('additional_files', []), ActivityAdditionalFields, activity_id, "additional_files")
        self.change_status_fields_check(data.get('images', []), ImageActivity, activity_id)
        self.change_status_fields_check(data.get('files', []), FileActivity, activity_id)

        if general_status:
            additional_status = ActivityAdditionalFields.objects.filter(activity_id=activity_id, status=False)
            if additional_status.exists():
                return False

            image_status = ImageActivity.objects.filter(activity_id=activity_id, status=False, archive=False)
            if image_status.exists():
                return False

            file_status = FileActivity.objects.filter(activity_id=activity_id, status=False, archive=False)
            if file_status.exists():
                return False
        return True

    @app_enable(PartProject.activity_create)
    def create(self, request, *args, **kwargs):
        data = copy.copy(request.data)
        data["student"] = request.user.id

        self.serializer_class = CreateActivitySerializer
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        with transaction.atomic():
            activity = serializer.save()
            # check selected files for additional fields any activity
            self.check_valid_additional_files(data=self.request.data)
            # save selected files for additional fields any activity
            self.save_files_additional_fields(activity, data=self.request.data)
            data = self.request.data
            self.check_valid_image_length(data)
            self.save_image(data.getlist('images[]', []), activity)
            self.save_file(data.getlist('files[]', []), activity)
            self.save_additional_field(json.loads(data.get('additional_fields[]', '[]')), activity)
            activity.updated_at = datetime.datetime.now()
            activity.save()

            # self.confirm_activity(activity)

        try:
            send_notification = threading.Thread(target=send_notification_teacher_activity, args=(activity,))
            send_notification.start()

        except Exception as e:
            logger_v1.error("send_notification_teacher_activity Error", extra={
                "detail": {
                    "error": e,
                }
            })

    @staticmethod
    def save_files_additional_fields(activity, data):
        # get all keys from request
        for key in data.keys():
            # get keys that start with additional_fields_files_
            if key.startswith("additional_fields_files_"):
                # get id additional_fields
                additional_field_id = str(key).split("_")[-2]

                # dir name for save files any additional fields
                file_location = settings.MEDIA_ROOT + "/additional_fields_files/" + str(activity.id) + "/" + str(additional_field_id) + "/"

                # if dir name not exist first create dir name
                if not os.path.exists(file_location):
                    os.makedirs(file_location)
                # else:
                #     # first delete previous dir name and files it
                #     shutil.rmtree(file_location)
                #     # create dir name
                #     os.makedirs(file_location)

                # get all files for one additional_fields
                for my_file in data.getlist(key, []):
                    # save file in dir by file system storage lib
                    fs = FileSystemStorage(location=file_location)
                    fs.save(my_file.name, my_file)

                    # file size
                    file_size = my_file.size
                    # 1 mb = 1024 * 1024
                    mb_size = 1024 * 1024

                    # get file information
                    file_info = {
                        "title": my_file.name,
                        "path": "/media/additional_fields_files/{0}/{1}/{2}".format(activity.id, additional_field_id, my_file.name),
                        "size": str(file_size // mb_size) + "mb" if file_size > mb_size else str(file_size // 1024) + "kb"
                    }
                    # save file in additional fields
                    activity_additional = ActivityAdditionalFields()
                    activity_additional.activity = activity
                    activity_additional.additional_field_id = additional_field_id
                    activity_additional.value = json.dumps(file_info)
                    activity_additional.save()

    def update_files_additional_fields(self, activity, data):
        # add new files added for additional fields
        self.save_files_additional_fields(activity, data)

        try:
            delete_files = json.loads(data.get('deleted_additional_files', '[]'))
        except Exception as e:
            logger_v1.error("Activity update_files Error", extra={
                "detail": {
                    "error": e,
                }
            })
            raise ValidationError(e, code=status.HTTP_400_BAD_REQUEST)

        if delete_files:
            # get all additional fields that selected for delete
            additional_fields = ActivityAdditionalFields.objects.filter(
                id__in=delete_files,
                activity_id=activity.id,
                status=False
            )
            if additional_fields:
                # delete files that previous upload for additional fields
                ActivityViewSet.delete_files_additional_from_path(activity, additional_fields)
                # delete additional fields
                additional_fields.delete()

    def check_for_accept_activity(self, activity):
        activity_id = activity.id
        activity = Activity.objects.filter(id=activity_id)
        bool_general = self.get_status_activity(activity)
        additional_field = ActivityAdditionalFields.objects.filter(activity_id=activity_id, status=False)
        image = ImageActivity.objects.filter(activity_id=activity_id, status=False, archive=False)
        file = FileActivity.objects.filter(activity_id=activity_id, status=False, archive=False)

        if not image and not additional_field and not file and bool_general:
            return True
        return False

    def update_images(self, data, activity):
        images = data.getlist('images[]', [])
        try:
            delete_images = json.loads(data.get('deleted_images', '[]'))
        except Exception as e:
            logger_v1.error("Activity update_images Error", extra={
                "detail": {
                    "error": e,
                }
            })
            raise ValidationError(e, code=status.HTTP_400_BAD_REQUEST)

        self.save_image(images, activity)
        if delete_images:
            _d_images = ImageActivity.objects.filter(
                id__in=delete_images,
                activity_id=activity.id,
                status=False,
                archive=False
            )
            if _d_images:
                _d_images.update(archive=True)

    def update_files(self, data, activity):
        files = data.getlist('files[]', [])
        self.save_file(files, activity)

        try:
            delete_files = json.loads(data.get('deleted_files', '[]'))
        except Exception as e:
            logger_v1.error("Activity update_files Error", extra={
                "detail": {
                    "error": e,
                }
            })
            raise ValidationError(e, code=status.HTTP_400_BAD_REQUEST)

        if delete_files:
            _d_images = FileActivity.objects.filter(
                id__in=delete_files,
                activity_id=activity.id,
                status=False,
                archive=False
            )
            if _d_images:
                _d_images.update(archive=True)

    def update_additional_field(self, data, _activity):
        activity = _activity.get()
        additional_fields = json.loads(data.get('additional_fields[]', '[]'))
        new_category = int(data.get('category', False))
        if new_category == activity.category_id and new_category:
            v = Validator(additional_fields_add_schema())
            for field in additional_fields:
                if not v.validate(field):
                    logger_v1.error("Activity update_additional_field Error", extra={
                        "detail": {
                            "error": v.errors,
                        }
                    })
                    raise ValidationError(v.errors, code=status.HTTP_400_BAD_REQUEST)
                query = ActivityAdditionalFields.objects.filter(
                    additional_field_id=field['id'],
                    activity_id=activity.id,
                )
                if query.filter(status=False):
                    # check additional field is drop_down
                    if query.filter(additional_field__field_type="drop_down"):
                        # delete previous additional fields if change drop down and any option have sub form
                        self.delete_previous_additional_fields(activity, field, query)

                    query.update(value=field['value'])
                else:
                    new_additional_field = AdditionalField.objects.filter(
                        category_id=activity.category_id,
                        id=field["id"]
                    )
                    if new_additional_field and not query.filter(status=True):
                        activity_additional = ActivityAdditionalFields()
                        activity_additional.activity = activity
                        activity_additional.additional_field_id = field["id"]
                        activity_additional.value = field['value']
                        activity_additional.save()
        elif not activity.category_status and new_category:
            _activity.update(category=new_category)
            self.remove_old_additional_field(activity)
            self.save_additional_field(additional_fields, activity, new_category)

        elif activity.category_status and not new_category:
            return
        else:
            logger_v1.error("Activity update_additional_field Error", extra={
                "detail": {
                    "error": CHANGE_CATEGORY_STATUS,
                }
            })
            raise ValidationError({"additional_fields": CHANGE_CATEGORY_STATUS}, code=status.HTTP_400_BAD_REQUEST)

    def delete_three_sub_form_additional_field(self, activity, additional_field_id):
        # this additional field is a drop down that have sub form
        combo_box_options = DropDownFormSomeAdditionalField.objects.filter(Q(additional_field_id=additional_field_id) & ~Q(group_select=None))
        if combo_box_options:
            # groups id combo box
            groups_id = combo_box_options.values_list('group_select', flat=True)
            # activity additional fields that previous save for other option this drop down
            pre_activity_additional_fields = ActivityAdditionalFields.objects.filter(additional_field__group_id__in=groups_id, activity=activity)
            # delete files that previous upload for pre additional fields
            self.delete_files_additional_from_path(activity=activity, additional_fields=pre_activity_additional_fields.filter(additional_field__field_type="file_upload"))
            pre_activity_additional_fields.delete()

    def delete_sub_form_additional_field(self, activity, additional_field_id):
        # this additional field is a drop down that have sub form
        combo_box_options = DropDownFormSomeAdditionalField.objects.filter(Q(additional_field_id=additional_field_id) & ~Q(group_select=None))
        if combo_box_options:
            for option in combo_box_options:
                for combo_box in AdditionalField.objects.filter(group__in=option.group_select.all(), field_type="drop_down"):
                    self.delete_three_sub_form_additional_field(activity, combo_box.id)
            # groups id combo box
            groups_id = combo_box_options.values_list('group_select', flat=True)
            # activity additional fields that previous save for other option this drop down
            pre_activity_additional_fields = ActivityAdditionalFields.objects.filter(additional_field__group_id__in=groups_id, activity=activity)
            # delete files that previous upload for pre additional fields
            self.delete_files_additional_from_path(activity=activity, additional_fields=pre_activity_additional_fields.filter(additional_field__field_type="file_upload"))
            pre_activity_additional_fields.delete()

    def delete_previous_additional_fields(self, activity, field, query):
        # this additional field is a drop down that have sub form
        combo_box_options = DropDownFormSomeAdditionalField.objects.filter(Q(additional_field_id=field['id']) & ~Q(group_select=None))
        if combo_box_options:
            # if change value this drop down
            if query[0].value != field['value']:
                # Todo later change this function recursive
                for option in combo_box_options:
                    for combo_box in AdditionalField.objects.filter(group__in=option.group_select.all(), field_type="drop_down"):
                        self.delete_sub_form_additional_field(activity, combo_box.id)
                # groups id combo box
                groups_id = combo_box_options.values_list('group_select', flat=True)
                # activity additional fields that previous save for other option this drop down
                pre_activity_additional_fields = ActivityAdditionalFields.objects.filter(additional_field__group_id__in=groups_id, activity=activity)
                # delete files that previous upload for pre additional fields
                self.delete_files_additional_from_path(activity=activity, additional_fields=pre_activity_additional_fields.filter(additional_field__field_type="file_upload"))
                pre_activity_additional_fields.delete()

    @staticmethod
    def get_point_student_from_emtiaz_activity(student_school, activity, rates_count):
        school_activity = activity.school

        if school_activity.county_id == student_school.county_id:
            coefficient = 1

        elif school_activity.province_id == student_school.province_id:
            coefficient = 2

        else:
            coefficient = 3

        point = POINT_EMTIAZ * coefficient

        if rates_count == 0:
            point *= 2

        return point

    @staticmethod
    def daily_student_point_change(student_id):
        today = datetime.datetime.today()
        today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)

        aggregate = RateActivity.objects.filter(
            student_id=student_id,
            created_at__range=(today_min, today_max)
        ).aggregate(Sum('point_student'))["point_student__sum"]

        sum_absolute = aggregate if aggregate is not None else 0

        try:
            act = StudentDailyReport.objects.get(date=today, student_id=int(student_id))
            act.point = sum_absolute
            act.save()
        except:
            StudentDailyReport(
                date=today,
                point=sum_absolute,
                student_id=int(student_id)
            ).save()

    @staticmethod
    def confirm_activity(activity, user_id):
        # confirm general fields
        activity.category_status = True
        activity.title_status = True
        activity.location_status = True
        activity.start_date_status = True
        activity.end_date_status = True
        activity.description_status = True

        # confirm images
        images = ImageActivity.objects.filter(activity=activity)
        for image in images:
            image.status = True
            image.save()

        # confirm files
        files = FileActivity.objects.filter(activity=activity)
        for file in files:
            file.status = True
            file.save()

        # confirm additional fields
        additional_fields = ActivityAdditionalFields.objects.filter(activity=activity)
        for add in additional_fields:
            add.status = True
            add.save()

        activity.state = "ACCEPT"
        activity.accepted_at = datetime.datetime.now()
        activity.checker_id = user_id

        activity.save()

        computing_point = threading.Thread(target=computing_point_activity, args=(activity.id,))
        computing_point.start()


class ActivityCategoryViewSet(BaseViewSet):
    queryset = ActivityCategory.objects.all()
    serializer_class = ActivityCategorySerializer

    # @method_decorator(cache_page(60 * 10))
    def list(self, request, *args, **kwargs):

        queryset = self.queryset.filter(status=True, hide_in_list_web=False)

        list_cat = []
        for cat in queryset:
            _dict_cat = {
                'id': cat.id,
                'title': cat.title,
                'slug': cat.slug,
                # 'groups': self._get_additional_fields_by_category(category_id=cat.id)
            }
            list_cat.append(_dict_cat)

        return Response({
            "results": list_cat,
            "count": len(list_cat),
            "next": None,
            "previous": None,
        })

    @list_route(methods=['get'], url_path='list_cat')
    # @method_decorator(cache_page(60 * 60 * 12))
    def list_cat(self, request, **kwargs):
        queryset = self.queryset.filter(status=True, hide_in_list_app=False)
        list_cat = []
        for cat in queryset:
            _dict_cat = {
                'id': cat.id,
                'title': cat.title,
            }
            list_cat.append(_dict_cat)

        return Response({
            "results": list_cat,
            "count": len(list_cat),
            "next": None,
            "previous": None,
        })

    @staticmethod
    def _get_additional_fields_by_category(category_id):
        additional_fields = AdditionalField.objects.filter(~Q(func_name="func3"), category_id=category_id)
        groups = GroupAdditionalFields.objects.all()
        list_valid_group = []
        try:
            for group in groups:
                list_additional_fields = []
                _dict_group = {
                    "id": group.id,
                    "order": group.order,
                    "label": group.label,
                }
                for add in additional_fields:
                    if add.group_id == group.id:
                        list_additional_fields.append(add)
                if list_additional_fields:
                    list_additional_fields = sorted(list_additional_fields, key=lambda x: x.order, reverse=False)
                    serializer = AdditionalFieldSerializer(list_additional_fields, many=True)
                    _dict_group["additional_fields"] = serializer.data
                    list_valid_group.append(_dict_group)

            list_valid_group = sorted(list_valid_group, key=lambda x: x["order"], reverse=False)
        except Exception as ex:
            print(ex)
        return list_valid_group

    # @method_decorator(cache_page(60 * 60 * 12))
    @detail_route(methods=['get'], url_path='additional_fields')
    def get_additional_fields_by_category(self, request, pk=None):
        additional_fields = AdditionalField.objects.filter(~Q(func_name="func3"), category_id=pk)
        groups = GroupAdditionalFields.objects.all()

        list_valid_group = []

        for group in groups:
            list_additional_fields = []
            _dict_group = {
                "id": group.id,
                "order": group.order,
                "label": group.label,
            }
            for add in additional_fields:
                if add.group_id == group.id and not add.group.child_group:
                    list_additional_fields.append(add)
            try:
                if list_additional_fields:
                    list_additional_fields = sorted(list_additional_fields, key=lambda x: x.order, reverse=False)
                    serializer = AdditionalFieldSerializer(list_additional_fields, many=True)
                    _dict_group["additional_fields"] = serializer.data
                    list_valid_group.append(_dict_group)
            except Exception as ex:
                pass

        list_valid_group = sorted(list_valid_group, key=lambda x: x["order"], reverse=False)
        return Response({
            "results": list_valid_group,
            "count": len(list_valid_group),
            "next": None,
            "province": None,
        })

    # @method_decorator(cache_page(60 * 60 * 12))
    @detail_route(methods=['get'], url_path='show_additional_fields')
    def show_additional_fields_by_category(self, request, pk=None):
        additional_fields = AdditionalField.objects.filter(~Q(func_name="func3"), category_id=pk)
        groups = GroupAdditionalFields.objects.all()

        list_valid_group = []

        for group in groups:
            list_additional_fields = []
            _dict_group = {
                "id": group.id,
                "order": group.order,
                "label": group.label,
            }
            for add in additional_fields:
                if add.group_id == group.id:
                    list_additional_fields.append(add)
            try:
                if list_additional_fields:
                    list_additional_fields = sorted(list_additional_fields, key=lambda x: x.order, reverse=False)
                    serializer = AdditionalFieldSerializer(list_additional_fields, many=True)
                    _dict_group["additional_fields"] = serializer.data
                    list_valid_group.append(_dict_group)
            except Exception as ex:
                pass

        list_valid_group = sorted(list_valid_group, key=lambda x: x["order"], reverse=False)
        return Response({
            "results": list_valid_group,
            "count": len(list_valid_group),
            "next": None,
            "province": None,
        })

    @detail_route(methods=['get'], url_path='get_sub_form')
    def get_sub_form_additional_fields(self, request, pk=None):
        groups_list = GroupAdditionalFields.objects.filter(dropdownformsomeadditionalfield=pk).values_list("id", flat=True)
        additional_fields = AdditionalField.objects.filter(group__in=groups_list)
        groups = GroupAdditionalFields.objects.all()

        list_valid_group = []

        for group in groups:
            list_additional_fields = []
            _dict_group = {
                "id": group.id,
                "order": group.order,
                "label": group.label,
            }
            for add in additional_fields:
                if add.group_id == group.id:
                    list_additional_fields.append(add)
            if list_additional_fields:
                list_additional_fields = sorted(list_additional_fields, key=lambda x: x.order, reverse=False)
                self.serializer_class = AdditionalFieldSerializer
                serializer = self.get_serializer(list_additional_fields, many=True)
                _dict_group["additional_fields"] = serializer.data
                list_valid_group.append(_dict_group)

        list_valid_group = sorted(list_valid_group, key=lambda x: x["order"], reverse=False)
        return Response({
            "results": list_valid_group,
            "count": len(list_valid_group),
            "next": None,
            "province": None,
        })


class AdditionalFieldViewSet(BaseViewSet):
    queryset = AdditionalField.objects.all()
    serializer_class = AdditionalFieldSerializer
    pagination_class = LargeResultsSetPagination

    # @method_decorator(cache_page(60 * 60 * 12))
    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(~Q(func_name="func3"))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)

            return response

        serializer = self.get_serializer(queryset, many=True)
        response = serializer.data

        return response


class GroupAdditionalFieldViewSet(BaseViewSet):
    queryset = GroupAdditionalFields.objects.all()
    serializer_class = GroupAdditionalFieldsSerializer
    pagination_class = LargeResultsSetPagination

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)


class ActivityReadOnlyViewSet(BaseViewSetReadOnly):
    queryset = Activity.objects.all()
    serializer_class = BoxActivitySerializer

    def list(self, request, *args, **kwargs):
        return Response([])

    @list_route(url_path='search', methods=['get'])
    @app_enable(PartProject.activity_search)
    def search(self, request):
        params = ActivityViewSet().get_params(request)
        query = self.get_query(request.user, params)
        orders = self.get_order(params, query)
        queryset = self.queryset.filter(query).order_by(*orders)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)

            return response

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @staticmethod
    def get_query(user, dict_params):
        user_type = get_user_type(user)
        q_object = Q()

        q_object.add(Q(state__in=['ACCEPT', 'TIL']), Q.AND)

        if 'province' in dict_params:
            q_object.add(Q(school__province_id=dict_params['province']), Q.AND)

        if 'category' in dict_params:
            q_object.add(Q(category_id=dict_params['category']), Q.AND)

        if 'department' in dict_params:
            q_object.add(Q(category__department_id=dict_params['department']), Q.AND)

        if 'county' in dict_params:
            q_object.add(Q(school__county_id=dict_params['county']), Q.AND)

        if 'text' in dict_params:
            q_object.add(Q(
                Q(title__regex=dict_params['text']) |
                Q(school__name__regex=dict_params['text'])
            ), Q.AND)

        if 'point_start' in dict_params:
            q_object.add(Q(point_emtiaz__gte=dict_params['point_start']), Q.AND)

        if 'point_end' in dict_params:
            q_object.add(Q(point_emtiaz__lte=dict_params['point_end']), Q.AND)

        if 'vip' in dict_params and dict_params['vip']:
            q_object.add(Q(vip=True), Q.AND)

        if 'school' in dict_params:
            q_object.add(Q(school_id=dict_params['school']), Q.AND)

        if user_type == "student":
            q_object.add(Q(gender=user.baseuser.gender), Q.AND)

            if 'my_school' in dict_params and dict_params['my_school']:
                q_object.add(Q(school_id=user.baseuser.student.school.id), Q.AND)
                q_object.add(~Q(state='BAN'), Q.AND)

        else:
            has_perm = has_perm_both_gender(user)
            if has_perm:
                gender_user = GENDER.get(dict_params.get("gender", user.baseuser.gender), user.baseuser.gender)

            else:
                gender_user = user.baseuser.gender

            q_object.add(Q(gender=gender_user), Q.AND)

        order = dict_params.get('order')
        if order == 'newest_province' or order == 'newest_county' or order == 'newest_camp':
            camp_id, county_id, province_id = get_user_location(user)

            if order == "newest_province":
                q_object.add(Q(school__province_id=province_id), Q.AND)

            elif order == "newest_county":
                q_object.add(Q(school__county_id=county_id), Q.AND)

            elif order == "newest_camp":
                q_object.add(Q(school__camp_id=camp_id), Q.AND)

        elif order == "newest_revolution":
            q_object.add(Q(category__slug="main_activity"), Q.AND)

        return q_object

    @staticmethod
    def get_order(dict_params, q_object):
        orders = []
        order = dict_params.get("order")
        if 'random' in dict_params or order == 'random':
            orders.append('?')

        if order == "most_view":
            orders.append('-view_count')

        if order == "point_high":
            orders.append('-point_emtiaz_sum')

        if order == "point_low":
            orders.append('point_emtiaz_sum')

        if order == "zero_point":
            q_object.add(Q(point_emtiaz__lte=0), Q.AND)
            orders.append('accepted_at')

        if order == "trend":
            q_object.add(Q(comments_count__gte=1), Q.AND)
            orders.append('-comments_count')

        if order == "newest":
            orders.append('-created_at')

        if not orders:
            orders.append('accepted_at')

        return orders

    @list_route(url_path='my_school', methods=['get'])
    def my_school(self, request):
        activity_year = self.get_activity_year(
            request.query_params.get('activity_year', 'default')
        )
        q_object = Q()
        q_object.add(Q(school_id=request.user.baseuser.student.school.id), Q.AND)
        # q_object.add(~Q(state='BAN'), Q.AND)
        if activity_year != 'default':
            q_object.add(Q(state='ACCEPT'), Q.AND)

        queryset = Activity.objects.using(activity_year).filter(
            q_object
        ).order_by('-created_at')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @staticmethod
    def get_activity_year(activity_year):
        if activity_year != '96_97':
            return 'default'
        return activity_year


class ActivityApiSadafViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Activity.objects.all()
    serializer_class = ActivityMainSerializer


class ActivityCategorySadafViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = ActivityCategory.objects.all()
    serializer_class = ActivityCategorySerializer


class SchoolSadafViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
