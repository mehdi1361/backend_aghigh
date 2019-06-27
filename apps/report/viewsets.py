import datetime
from django.db.models.functions import ExtractHour, ExtractWeekDay, TruncDay
from django.db.models import Q, Avg, Count, F, Sum
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import list_route

from apps.common.utils import gregorian_to_persian_chart, gregorian_to_persian
from apps.common.viewsets import BaseViewSet, BaseViewSetReadOnly
from apps.activity.serializers import BoxActivitySerializer
from apps.activity.models import Activity, Department
from apps.league.serializer import LeagueSerializer
from apps.league.models import School
from apps.league.models import Province, County, Camp
from apps.report.models import Reports
from apps.report.serializers import ReportsSerializer
from apps.report.static import WEEK_DAYS
from apps.user.models.base import BaseUser
from dashboard.mongo_db import cursor


class ReportsViewSet(BaseViewSetReadOnly):
    serializer_class = ReportsSerializer
    queryset = Reports.objects.all()

    @list_route(url_path='last', methods=['get'])
    def report_last(self, request):
        report_last = self.queryset.last()
        data = self.get_serializer(report_last).data

        return Response(data, status.HTTP_200_OK)


class ActivityReportViewSet(BaseViewSetReadOnly):
    serializer_class = BoxActivitySerializer
    queryset = Activity.objects.all()

    @list_route(url_path='province', methods=['get'])
    def province_activity(self, request):
        try:
            code = request.query_params["code"]
        except:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        province_activity = self.queryset.filter(school__province__code=code)

        data = {
            "accept": {
                "male": province_activity.filter(state='ACCEPT', gender="male").count(),
                "female": province_activity.filter(state='ACCEPT', gender="female").count()
            },
            "not_accept": {
                "male": province_activity.filter(~Q(state='ACCEPT'), gender="male").count(),
                "female": province_activity.filter(~Q(state='ACCEPT'), gender="female").count()
            },
            "shr_not_accept": {
                "male": province_activity.filter(state__in=['SHR', 'NEW'], gender="male").count(),
                "female": province_activity.filter(state__in=['SHR', 'NEW'], gender="female").count()
            },
            "she_not_accept": {
                "male": province_activity.filter(state='SHE', gender="male").count(),
                "female": province_activity.filter(state='SHE', gender="female").count()
            }
        }

        return Response(data, status=status.HTTP_200_OK)

    @list_route(url_path='average_difference', methods=['get'])
    def average_difference(self, request):
        ac_queryset = self.queryset.filter(state="ACCEPT").values(
            'school__province__code',
            "school__province__title",
        ).annotate(Count('id'), sum_difference=Sum(F('accepted_at') - F('created_at')))

        ac_all_queryset = self.queryset.values(
            'school__province__code',
        ).annotate(Count('id'))

        # clean_dict = copy.deepcopy(PROVINCE_DATA)
        clean_dict = {}
        for ac in ac_queryset:
            if ac["id__count"]:
                if ac["school__province__code"] not in clean_dict:
                    clean_dict[ac["school__province__code"]] = {
                        "province_name": ac["school__province__title"],
                        "average_difference": 0,
                        "count": 0,
                    }
                if ac["sum_difference"] is not None:
                    count = 1
                    for province in ac_all_queryset:
                        if ac["school__province__code"] == province['school__province__code']:
                            count = province["id__count"]
                            break

                    clean_dict[ac["school__province__code"]]["average_difference"] = round((ac["sum_difference"].days + (ac["sum_difference"].seconds / 3600 / 24)) / count, 2)

                else:
                    clean_dict[ac["school__province__code"]]["average_difference"] = 0

                clean_dict[ac["school__province__code"]]["count"] = ac["id__count"]

        return Response(dict(clean_dict), status=status.HTTP_200_OK)

    @list_route(url_path='provinces', methods=['get'])
    def provinces_activity(self, request):
        ac_queryset = self.queryset.values(
            'school__province__code',
            "school__province__title",
            "student__gender"
        ).annotate(Count('id'))

        clean_dict = {}
        for ac in ac_queryset:
            if ac["id__count"]:
                if ac["school__province__code"] not in clean_dict:
                    clean_dict[ac["school__province__code"]] = {
                        "province_name": ac["school__province__title"],
                        "male": 0,
                        "female": 0
                    }

                clean_dict[ac["school__province__code"]][ac["student__gender"]] = ac["id__count"]

        return Response(dict(clean_dict), status=status.HTTP_200_OK)

    #  تابع زیر دیتای مورد نیاز برای نمودارهای تاریخ ثبت فعالیت را بر اساس نوع نمودار آماده می کند
    @method_decorator(cache_page(60 * 60 * 1))
    @list_route(url_path='dateـregister', methods=['get'])
    def date_register_activity(self, request):
        report_type = self.request.query_params.get("report_type", None)
        if report_type not in ['hour', 'week', 'month', 'day']:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        queryset = self.set_activity_report_queryset(self.request.query_params, filter_start_date='created_at__gte',
                                                     filter_end_date='created_at__lte')
        results = []
        if report_type == "hour":
            results = queryset.annotate(
                axis_x=ExtractHour('created_at')
            ).values('axis_x').annotate(count=Count('id')).order_by("axis_x")
            results = list(results)

        elif report_type == "week":
            results = queryset.annotate(
                axis_x=ExtractWeekDay('created_at')
            ).values('axis_x').annotate(count=Count('id')).order_by("axis_x")

            week_days = WEEK_DAYS.copy()
            # map data for result
            for report_item in results:
                day_value = (report_item['axis_x'] % 7) + 1
                report_item['axis_x'] = day_value
                report_item['sort_key'] = day_value
                report_item['axis_x'] = week_days[str(report_item['axis_x'])]

            results = sorted(results, key=lambda k: k['sort_key'])

        elif report_type == "day":
            results = list(queryset.annotate(
                axis_x=TruncDay('created_at')
            ).values('axis_x').annotate(count=Count('id')).order_by("axis_x"))
            for report_item in results:
                report_item['axis_x'] = gregorian_to_persian_chart(report_item['axis_x'])

        return Response(results, status=status.HTTP_200_OK)

    @method_decorator(cache_page(60 * 60 * 1))
    @list_route(url_path='date_done', methods=['get'])
    def date_done_activity(self, request):
        report_type = self.request.query_params.get("report_type", None)
        if report_type not in ['hour', 'week', 'month', 'day']:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        queryset = self.set_activity_report_queryset(self.request.query_params)
        results = []
        if report_type == "hour":
            results = queryset.annotate(
                axis_x=ExtractHour('start_date')
            ).values('axis_x').annotate(count=Count('id')).order_by("axis_x")
            results = list(results)

        elif report_type == "week":
            results = queryset.annotate(
                axis_x=ExtractWeekDay('start_date')
            ).values('axis_x').annotate(count=Count('id')).order_by("axis_x")

            week_days = WEEK_DAYS.copy()
            # map data for result
            for report_item in results:
                day_value = (report_item['axis_x'] % 7) + 1
                report_item['axis_x'] = day_value
                report_item['sort_key'] = day_value
                report_item['axis_x'] = week_days[str(report_item['axis_x'])]

            results = sorted(results, key=lambda k: k['sort_key'])

        elif report_type == "day":
            results = list(queryset.annotate(
                axis_x=TruncDay('start_date')
            ).values('axis_x').annotate(count=Count('id')).order_by("axis_x"))

            for report_item in results:
                report_item['axis_x'] = gregorian_to_persian(report_item['axis_x'])

        return Response(results, status=status.HTTP_200_OK)

    @method_decorator(cache_page(60 * 60 * 1))
    @list_route(url_path='date_accept', methods=['get'])
    def date_accept_activity(self, request):
        report_type = self.request.query_params.get("report_type", None)
        results = []
        if report_type not in ['hour', 'week', 'month', 'day']:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        queryset = self.set_activity_report_queryset(
            self.request.query_params,
            filter_start_date='accepted_at__gte',
            filter_end_date='accepted_at__lte'
        )
        queryset = queryset.filter(~Q(accepted_at=None))

        if report_type == "hour":
            results = queryset.annotate(
                axis_x=ExtractHour('accepted_at')
            ).values('axis_x').annotate(count=Count('id')).order_by("axis_x")
            results = list(results)

        elif report_type == "week":
            results = queryset.annotate(
                axis_x=ExtractWeekDay('accepted_at')
            ).values('axis_x').annotate(count=Count('id')).order_by("axis_x")

            week_days = WEEK_DAYS.copy()
            # map data for result
            for report_item in results:
                day_value = (report_item['axis_x'] % 7) + 1
                report_item['axis_x'] = day_value
                report_item['sort_key'] = day_value
                report_item['axis_x'] = week_days[str(report_item['axis_x'])]

            results = sorted(results, key=lambda k: k['sort_key'])

        elif report_type == "day":
            results = list(queryset.annotate(
                axis_x=TruncDay('accepted_at')
            ).values('axis_x').annotate(count=Count('id')).order_by("axis_x"))
            for report_item in results:
                report_item['axis_x'] = gregorian_to_persian_chart(report_item['axis_x'])

        return Response(results, status=status.HTTP_200_OK)

    @staticmethod
    def set_activity_report_queryset(query_params, filter_start_date="start_date__gte", filter_end_date="start_date__lte"):
        filter_items = {}
        gender = query_params.get("gender", None)
        province = query_params.get("province", None)
        county = query_params.get("county", None)
        camp = query_params.get("camp", None)
        school = query_params.get("school", None)
        category = query_params.get("category", None)
        start_date = query_params.get("start_date", None)
        end_date = query_params.get("end_date", None)

        if province and province.isdigit():
            filter_items['school__province_id'] = province

        if county and county.isdigit():
            filter_items['school__county_id'] = county

        if camp and camp.isdigit():
            filter_items['school_camp_id'] = camp

        if school and school.isdigit():
            filter_items['school'] = school

        if category and category.isdigit():
            filter_items['category'] = category

        if gender in ['male', 'female', 'both']:
            if gender != "both":
                filter_items['gender'] = gender

        if start_date:
            filter_items[filter_start_date] = start_date

        if end_date:
            filter_items[filter_end_date] = end_date

        queryset = Activity.objects.filter(**filter_items)

        return queryset

    @list_route(url_path='activity_cat_dep', methods=['get'])
    def activity_cat_dep(self, request):
        q_object = Q()
        q_object.add(Q(state="ACCEPT"), Q.AND)

        if 'gender' in request.query_params:
            q_object.add(Q(gender=request.query_params['gender']), Q.AND)

        if 'province' in request.query_params:
            q_object.add(Q(school__province_id=request.query_params['province']), Q.AND)

        if 'county' in request.query_params:
            q_object.add(Q(school__county_id=request.query_params['county']), Q.AND)

        departments = list(Department.objects.all())
        activities_cat = self.queryset.filter(q_object).values(
            'category_id',
            'category__title',
            'category__department_id'
        ).annotate(Count('id'))

        cleaned_data = []
        for item in departments:
            categories = []
            department_dict = {
                "title": item.title,
                "id": item.id,
                'count': 0
            }
            for act in activities_cat:
                if item.id == act["category__department_id"]:
                    categories.append(dict(
                        title=act["category__title"],
                        count=act["id__count"],
                    ))
                    department_dict["count"] += act["id__count"]

            if department_dict["count"]:
                department_dict["categories"] = categories

                cleaned_data.append(department_dict)

        return Response(data=cleaned_data, status=status.HTTP_200_OK)


class UserReportViewSet(BaseViewSetReadOnly):
    @method_decorator(cache_page(60 * 60 * 1))
    def list(self, request, *args, **kwargs):
        cache_date = gregorian_to_persian_chart(datetime.datetime.now(), str_type="%Y/%m/%d %H:%M")  # تاریخ ساخت گزارش
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        province = request.query_params.get('province')
        county = request.query_params.get('county')

        q_object = {}
        if end_date:
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            q_object["requested_at"] = {"$lte": end_date}

        if start_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            q_object["requested_at"] = {"$gte": start_date}

        query_set = list(cursor.rest_log.distinct('user_id', q_object))
        query_set_sql = BaseUser.objects.filter(id__in=query_set)

        female, male = self.get_student_visit(county, province, query_set_sql)
        teachers = self.get_teachers_visit_count(county, province, query_set_sql)

        dict_report = {
            "male": male,
            "female": female,
            "teachers": teachers,
            "all_user": male + female + teachers,
            "cache_date": cache_date,
        }
        return Response(dict_report, status=status.HTTP_200_OK)

    @staticmethod
    def get_student_visit(county, province, query_set):
        exclude_student = Q()
        if province:
            exclude_student.add(~Q(student__school__province_id=province), Q.AND)
        if county:
            exclude_student.add(~Q(student__school__county_id=county), Q.AND)

        if exclude_student.children:
            male = query_set.filter(gender="male").exclude(exclude_student).distinct().count()
            female = query_set.filter(gender="female").exclude(exclude_student).distinct().count()

        else:
            male = query_set.filter(gender="male").exclude(student__isnull=True).distinct().count()
            female = query_set.filter(gender="female").exclude(student__isnull=True).distinct().count()

        return female, male

    @staticmethod
    def get_teachers_visit_count(county, province, query_set):
        list_teachers = []
        if province and not county:
            list_teachers.extend(list(Province.objects.get(id=province).coaches.all().values("id")))
            list_teachers.extend(list(County.objects.filter(province_id=province).extra(select={'coach_id': 'id'}).values('id')))
            list_teachers.extend(list(Camp.objects.filter(county__province_id=province).extra(select={'coach_id': 'id'}).values('id')))
            list_teachers.extend(list(School.objects.filter(province_id=province).extra(select={'teacher_id': 'id'}).values('id')))

        if county:
            list_teachers.extend(list(County.objects.filter(id=county).extra(select={'coach_id': 'id'}).values('id')))
            list_teachers.extend(list(Camp.objects.filter(county_id=county).extra(select={'coach_id': 'id'}).values('id')))

        if list_teachers:
            list_teachers_id = []
            for item in list_teachers:
                list_teachers_id.append(item["id"])

            return query_set.filter(id__in=list_teachers_id).values("user").distinct().count()

        return query_set.exclude(teacher__isnull=True).values("user").distinct().count()


class SchoolReportViewSet(BaseViewSetReadOnly):
    queryset = School.objects.all()
    serializer_class = LeagueSerializer

    def list(self, request, *args, **kwargs):
        pass

    @list_route(url_path='province_ranking', methods=['get'])
    def province_ranking(self, request):
        gender = request.query_params.get('gender', request.user.baseuser.gender)
        if gender != 'both':
            ac_queryset = self.queryset.filter(~Q(province__code="123456789"), gender=gender, active=True).values(
                'province__code',
                "province__title",
            ).annotate(Avg('point'), Count('id')).order_by("-point__avg")
        else:
            ac_queryset = self.queryset.filter(~Q(province__code="123456789"), active=True).values(
                'province__code',
                "province__title",
            ).annotate(Avg('point'), Count('id')).order_by("-point__avg")

        clean_list = []
        rank = 1
        for ac in ac_queryset:
            clean_list.append({
                "province_name": ac["province__title"],
                "province_code": ac["province__code"],
                "point": round(ac["point__avg"], 2),
                "rank": rank,
                "count_school_active": 0,
                "count_all_school": ac["id__count"],
            })
            rank += 1

        if gender != 'both':
            act_school_province = Activity.objects.filter(
                ~Q(school__province__code="123456789"),
                state="ACCEPT",
                school__gender=gender
            ).values('school_id', 'school__province__code').distinct('school_id')
        else:
            act_school_province = Activity.objects.filter(
                ~Q(school__province__code="123456789"),
                state="ACCEPT",
            ).values('school_id', 'school__province__code').distinct('school_id')

        for item in act_school_province:
            for ac in clean_list:
                if ac['province_code'] == item['school__province__code']:
                    ac['count_school_active'] += 1

        return Response(clean_list, status=status.HTTP_200_OK)
