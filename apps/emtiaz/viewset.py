import json
import datetime
import jdatetime
import threading

from cerberus import Validator
from django.db.models import Sum, Count, Q
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import detail_route, list_route

from apps.activity.static import GENDER
from apps.activity.viewsets import ActivityReadOnlyViewSet
from apps.common.app_enable import app_enable
from apps.common.utils import PartProject
from apps.emtiaz import static
from apps.league.models import Department
from apps.emtiaz.serializer import CreateActivityCommentSerializer, ParamSerializer, ShowCommentSerializer
from apps.emtiaz.models import Param, ActivityComment, ParamActivityComment, SumActivityParam
from apps.common.viewsets import BaseViewSet, LargeResultsSetPagination
from apps.emtiaz.schema import activity_param_add_schema
from apps.activity.serializers import BoxActivitySerializer
from apps.activity.models import Activity, ActivityDailyReport, StudentDailyReport, ActivityCategory
from apps.user.models.student import Student
from apps.user.serializers import SchoolSerializer
from utils.user_type import get_user_type, get_user_level, get_user_location, has_perm_both_gender


class ParamViewSet(BaseViewSet):
    serializer_class = ParamSerializer
    queryset = Param.objects.all()
    pagination_class = LargeResultsSetPagination


class ActivityCommentViewSet(BaseViewSet):
    queryset = ActivityComment.objects.all()
    serializer_class = ShowCommentSerializer

    @detail_route(methods=['get'], url_path='activity')
    def get_comment_by_activity_id(self, request, pk=None):
        activity_year = ActivityReadOnlyViewSet.get_activity_year(
            request.query_params.get('activity_year', 'default')
        )
        queryset = ActivityComment.objects.using(activity_year).filter(activity_id=pk)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @app_enable(PartProject.activity_comment)
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        sender = ActivityComment.objects.filter(sender=request.user.id, activity_id=data.get("activity", 0))
        if not sender:
            self.serializer_class = CreateActivityCommentSerializer
            data['sender'] = request.user.id
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({"status": status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_423_LOCKED)

    def update(self, request, *args, **kwargs):
        self.serializer_class = CreateActivityCommentSerializer
        data = request.data.copy()
        data['sender'] = request.user.id
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @transaction.atomic()
    def perform_update(self, serializer):
        comment = serializer.save()
        data = self.request.data

        thread_worker = threading.Thread(target=self.save_param, args=(data, comment))
        thread_worker.start()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @transaction.atomic()
    def perform_create(self, serializer):
        comment = serializer.save()
        data = self.request.data
        thread_worker = threading.Thread(target=self.save_param, args=(data, comment))
        thread_worker.start()

    @staticmethod
    def save_param(data, comment):
        params = data.get('params', '[]')
        try:
            params = json.loads(params)
        except Exception as e:
            raise ValidationError(e, code=status.HTTP_400_BAD_REQUEST)

        db_params = Param.objects.all().count()
        if db_params != len(params):
            raise ValidationError({"params": "error"}, code=status.HTTP_400_BAD_REQUEST)

        v = Validator(activity_param_add_schema())
        for param in params:
            if not v.validate(param):
                raise ValidationError(v.errors, code=status.HTTP_400_BAD_REQUEST)

            _param_model = ParamActivityComment.objects.filter(
                param_id=param['id'],
                activity_comment=comment
            )

            if _param_model.exists():
                param_model = _param_model.get()
            else:
                param_model = ParamActivityComment()

            param_model.activity_comment = comment
            param_model.param_id = param['id']
            param_model.value = param['value']
            param_model.save()

            ActivityCommentViewSet.update_sum_activity(data, param)

    @staticmethod
    def update_sum_activity(data, param):
        obj = SumActivityParam.objects.filter(
            activity_id=int(data['activity']),
            param_id=param['id']
        )
        if not obj:
            obj.create(
                activity_id=int(data['activity']),
                param_id=param['id'],
                sum=param['value'],
                count=1
            )
        else:
            param_act = ParamActivityComment.objects.filter(
                param_id=param['id'],
                activity_comment__activity_id=int(data['activity'])
            ).aggregate(Sum('value'), Count('id'))

            obj.update(
                sum=param_act["value__sum"],
                count=param_act["id__count"]
            )


class EmtiazViewSet(BaseViewSet):
    queryset = Activity.objects.all()
    serializer_class = BoxActivitySerializer

    def list(self, request, *args, **kwargs):
        res = []
        user_type = get_user_type(request.user)
        has_perm = has_perm_both_gender(request.user)

        if has_perm:
            gender_user = GENDER.get(request.query_params.get('gender', request.user.baseuser.gender), request.user.baseuser.gender)

        else:
            gender_user = request.user.baseuser.gender

        if user_type == "student":
            self.newest_resanesh_festival(res, gender_user)

            self.newest_revolution_school(res, gender_user)

            self.newest_activity(res, gender_user)

            self.most_point_activity(res, gender_user)

            student = Student.objects.filter(id=request.user.id).select_related('school')
            if student.exists():
                student = student.get()

                province_id = student.school.province_id
                self.newest_province_activity(res, province_id, gender_user)

                county_id = student.school.county_id
                self.newest_county_activity(res, county_id, gender_user)

                camp_id = student.school.camp_id
                self.newest_camp_activity(res, camp_id, gender_user)

        elif user_type == "teacher":
            self.newest_resanesh_festival(res, gender_user)

            self.newest_revolution_school(res, gender_user)

            self.newest_activity(res, gender_user)

            self.most_point_activity(res, gender_user)

            levels = get_user_level(request.user, "teacher")
            camp_id, county_id, province_id = get_user_location(request.user, levels)

            if camp_id:
                self.newest_camp_activity(res, camp_id, gender_user)

            if county_id:
                self.newest_county_activity(res, county_id, gender_user)

            if province_id:
                self.newest_province_activity(res, province_id, gender_user)

        return Response({
            "next": None,
            "previous": None,
            "count": len(res),
            "results": res
        })

    # @method_decorator(cache_page(60 * 10))
    def newest_activity(self, res, gender):
        activities = self.queryset.filter(
            state__in=['ACCEPT', 'TIL'],
            gender=gender,
        ).order_by("-accepted_at")[:12]

        _dict = {
            "id": 2,
            "order": 'newest',
            "title": "تازه ترین ها",
            "activities": self.get_serializer(activities, many=True).data,
            "category": 0
        }
        if _dict['activities']:
            res.append(_dict)

    def newest_revolution_school(self, res, gender):
        activities = self.queryset.filter(
            category__slug="main_activity",
            state__in=['ACCEPT', 'TIL'],
            gender=gender,
        ).order_by("-accepted_at")[:12]
        _dict = {
            "id": 1,
            "order": 'newest_revolution',
            "title": "تازه ترین های مدرسه انقلاب",
            "activities": self.get_serializer(activities, many=True).data,
            "category": ActivityCategory.objects.get(slug="main_activity").id
        }
        if _dict['activities']:
            res.append(_dict)

    def newest_resanesh_festival(self, res, gender):
        activities = self.queryset.filter(
            category__slug="resanesh",
            state__in=['ACCEPT', 'TIL'],
            gender=gender,
        ).order_by("-accepted_at")[:12]
        _dict = {
            "id": 1,
            "order": 'newest_resanesh',
            "title": "جدیدترین فعالیت های رسانش",
            "activities": self.get_serializer(activities, many=True).data,
            "category": ActivityCategory.objects.get(slug="resanesh").id
        }
        if _dict['activities']:
            res.append(_dict)

    # @method_decorator(cache_page(60 * 60 * 1))
    def most_point_activity(self, res, gender):
        activities = self.queryset.filter(
            state__in=['ACCEPT', 'TIL'],
            gender=gender,
        ).order_by("-point_emtiaz_sum")[:12]

        _dict = {
            "id": 3,
            "order": 'point_high',
            "title": " پرامتیازترین های 7 روز گذشته",
            "activities": self.get_serializer(activities, many=True).data,
            "category": 0
        }
        if _dict['activities']:
            res.append(_dict)

    def newest_province_activity(self, res, province_id, gender):
        activities = self.queryset.filter(
            school__province_id=province_id,
            gender=gender,
            state__in=['ACCEPT', 'TIL']
        ).order_by("-accepted_at")[:12]

        _dict = {
            "id": 4,
            "order": 'newest_province',
            "title": "جدیدترین های استان من",
            "activities": self.get_serializer(activities, many=True).data,
            "category": 0
        }
        if _dict['activities']:
            res.append(_dict)

    def newest_county_activity(self, res, county_id, gender):
        activities = self.queryset.filter(
            school__county_id=county_id,
            gender=gender,
            state__in=['ACCEPT', 'TIL']
        ).order_by("-accepted_at")[:12]

        _dict = {
            "id": 5,
            "order": 'newest_county',
            "title": "جدیدترین های شهر من",
            "activities": self.get_serializer(activities, many=True).data,
            "category": 0
        }
        if _dict['activities']:
            res.append(_dict)

    def newest_camp_activity(self, res, camp_id, gender):
        activities = self.queryset.filter(
            school__camp_id=camp_id,
            gender=gender,
            state__in=['ACCEPT', 'TIL']
        ).order_by("-accepted_at")[:12]

        _dict = {
            "id": 6,
            "order": 'newest_camp',
            "title": "جدیدترین های قرارگاه من",
            "activities": self.get_serializer(activities, many=True).data,
            "category": 0
        }
        if _dict['activities']:
            res.append(_dict)

    def retrieve(self, request, *args, **kwargs):
        pk = int(kwargs.get("pk"))
        gender_user = request.user.baseuser.gender
        activities = self.queryset

        if pk == 2:
            title = "تازه ترین ها"
            activities = activities.filter(
                gender=gender_user,
                state__in=['ACCEPT', 'TIL']
            ).order_by("-accepted_at")[:12]

        elif pk == 3:
            title = "پرامتیازترین ها"
            activities = activities.filter(
                gender=gender_user,
                state__in=['ACCEPT', 'TIL']
            ).order_by("-point")[:12]

        elif pk == 4:
            title = "جدیدترین های استان من"
            student = Student.objects.filter(id=request.user.id).select_related('school')
            if student:
                province_id = student.get().school.province.id
                activities = activities.filter(
                    school__province_id=province_id,
                    gender=gender_user,
                    state__in=['ACCEPT', 'TIL']
                ).order_by("-accepted_at")[:12]
        else:

            return Response(status=status.HTTP_400_BAD_REQUEST)

        result = {
            "name": title,
            "id": pk,
            "activities": self.get_serializer(activities, many=True).data
        }

        return Response(result)

    @list_route(url_path='special_filters', methods=['get'])
    def get_special_filters(self, request):
        has_perm = has_perm_both_gender(request.user)

        if has_perm:
            gender_user = GENDER.get(request.query_params.get('gender', request.user.baseuser.gender), request.user.baseuser.gender)

        else:
            gender_user = request.user.baseuser.gender

        list_special_filters = {

            "activity": [
                {
                    "title": "برترین فعالیت های علمی درسی",
                    "color": "#9c27b0",
                    "action": "department",
                    "icon": "",
                    "param": "department=1&gender={0}".format(gender_user)
                },
                {
                    "title": "برترین فعالیت های عقیدتی معرفتی",
                    "color": "#db4437",
                    "action": "department",
                    "icon": "",
                    "param": "department=2&gender={0}".format(gender_user)
                },
                {
                    "title": "برترین فعالیت های فرهنگی سیاسی اجتماعی",
                    "color": "#e91e63",
                    "action": "department",
                    "icon": "",
                    "param": "department=3&gender={0}".format(gender_user)
                },
                {
                    "title": "برترین فعالیت های کندوی کتاب",
                    "color": "#009688",
                    "action": "category",
                    "icon": "",
                    "param": "category=34&gender={0}".format(gender_user)
                },
                {
                    "title": "برترین فعالیت های طرح انسجام",
                    "color": "#673ab7",
                    "action": "category",
                    "icon": "",
                    "param": "category=33&gender={0}".format(gender_user)
                },
                {
                    "title": "برترین فعالیت های مدرسه انقلاب",
                    "color": "#9c27b0",
                    "action": "category",
                    "icon": "",
                    "param": "category=35&gender={0}".format(gender_user)
                },
                {
                    "title": "پر طرفدارترین برنامه هفته",
                    "color": "#009688",
                    "action": "weekly_activity",
                    "icon": "",
                    "param": "gender={0}".format(gender_user)
                },
                {
                    "title": "پر طرفدار ترین برنامه روز",
                    "color": "#e91e63",
                    "action": "daily_activity",
                    "icon": "",
                    "param": "gender={0}".format(gender_user)
                },
                {
                    "title": "سریع ترین فعالیت ثبت شده در ماه",
                    "color": "#e91e63",
                    "action": "fast_activity",
                    "icon": "",
                    "param": "gender={0}".format(gender_user)
                }
            ],
            "personal": [
                {
                    "title": "برترین امتیاز بگیرهای این ماه",
                    "color": "#673ab7",
                    "action": "person",
                    "icon": "",
                    "param": "gender={0}".format(gender_user)
                }
            ]
        }

        return Response(data=list_special_filters, status=status.HTTP_200_OK)

    @list_route(url_path='specific_activity', methods=['get'])
    def get_specific_activity(self, request):
        dict_params = request.query_params
        has_perm = has_perm_both_gender(request.user)

        if has_perm:
            gender_user = GENDER.get(request.query_params.get('gender', request.user.baseuser.gender), request.user.baseuser.gender)

        else:
            gender_user = request.user.baseuser.gender

        q_object = Q()

        q_object.add(Q(state__in=['ACCEPT', 'TIL']), Q.AND)
        q_object.add(Q(gender=gender_user), Q.AND)
        date_now = datetime.datetime.now()

        if 'action' not in dict_params and dict_params["action"] not in static.LIST_ACTION:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
            )

        if dict_params["action"] == "category" and 'category' in dict_params:
            q_object.add(Q(category_id=dict_params['category']), Q.AND)
            queryset = self.queryset.filter(q_object).order_by('-point_emtiaz_sum')[:10]
            try:
                title = "برترین فعالیت های {0}".format(ActivityCategory.objects.get(id=dict_params['category']).title)
            except:
                title = "category not found"

        elif dict_params["action"] == "department" and 'department' in dict_params:
            q_object.add(Q(category__department_id=dict_params['department']), Q.AND)
            queryset = self.queryset.filter(q_object).order_by('-point_emtiaz_sum')[:10]
            try:
                title = "برترین فعالیت های {0}".format(Department.objects.get(id=dict_params['department']).title)
            except:
                title = "department not found"

        elif dict_params["action"] == "daily_activity":
            today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
            today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)

            _activity = ActivityDailyReport.objects.filter(
                activity__gender=gender_user,
                date__range=(today_min, today_max)
            ).order_by('-point')

            list_id = []
            for ac_id in _activity:
                list_id.append(ac_id.activity_id)

            queryset = self.queryset.filter(id__in=list_id).order_by('-point_emtiaz_sum')[:10]
            title = "برترین فعالیت های روز"

        elif dict_params["action"] == "weekly_activity":
            week_day = jdatetime.datetime.now().weekday()
            activities = ActivityDailyReport.objects.filter(
                activity__gender=gender_user,
                date__gte=date_now - datetime.timedelta(days=week_day),
                date__lte=date_now + datetime.timedelta(days=(6 - week_day))
            ).order_by('-point')
            list_id = []
            for ac_id in activities:
                list_id.append(ac_id.activity_id)

            queryset = self.queryset.filter(id__in=list_id).order_by('-point_emtiaz_sum')[:10]
            title = "برترین فعالیت های هفته"

        elif dict_params["action"] == "fast_activity":
            day = jdatetime.datetime.now().day
            queryset = sorted(self.queryset.filter(
                gender=gender_user,
                accepted_at__gte=date_now - datetime.timedelta(days=day),
                accepted_at__lte=date_now + datetime.timedelta(days=(30 - day))
            ), key=lambda t: t.different_date, reverse=True)[:10]

            title = "سریع ترین فعالیت های ثبت شده در این ماه"

        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "results": serializer.data,
            "title": title,
        })

    @list_route(url_path='specific_student', methods=['get'])
    def get_specific_student(self, request):
        has_perm = has_perm_both_gender(request.user)

        if has_perm:
            gender_user = GENDER.get(request.query_params.get('gender', request.user.baseuser.gender), request.user.baseuser.gender)

        else:
            gender_user = request.user.baseuser.gender

        date_now = datetime.datetime.now()
        day = jdatetime.datetime.now().day

        students = StudentDailyReport.objects.filter(
            student__gender=gender_user,
            date__gte=date_now - datetime.timedelta(days=day),
            date__lte=date_now + datetime.timedelta(days=(30 - day))
        ).values(
            'student',
        ).annotate(Sum('point')).order_by("-point__sum")[:3]

        list_student = []
        for student in students:
            try:
                student_data = Student.objects.get(id=student["student"])
                dict_student = {
                    "first_name": student_data.first_name,
                    "last_name": student_data.last_name,
                    "school": SchoolSerializer(student_data.school, many=False, read_only=True).data,
                    "gender": student_data.gender,
                    "point": student["point__sum"],
                }
                try:
                    dict_student["image"] = "/" + student_data.image.url
                except:
                    dict_student["image"] = ""

                list_student.append(dict_student)
            except:
                pass

        return Response(list_student)

    @list_route(url_path='student_point', methods=['get'])
    def student_point(self, request):

        students = StudentDailyReport.objects.filter(
            student__username=request.user.baseuser.username
        ).aggregate(Sum("point"))

        return Response(data={"student_point": students['point__sum']})
