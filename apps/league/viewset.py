import copy

from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from apps.activity.static import GENDER
from utils.user_type import get_user_type, has_perm_both_gender, get_user_location_role
from apps.common.viewsets import BaseViewSet, LargeResultsSetPagination
from apps.league.models import Province, County, Camp
from apps.user.models.student import Student, School
from apps.league.static import (
    list_column_league_student,
    list_column_league_teacher,
    MIN_POINT_CITIZEN,
    MIN_SAME_POINT,
    MAX_SAME_POINT,
    MIN_POINT_PROVINCIAL,
    list_column_league_province, list_column_league_country)
from apps.league.serializer import (
    LeagueSerializer,
    SchoolTeacherSerializer,
    ProvinceSerializer,
    OtherSchoolSerializer,
    CountySerializer,
    CampSerializer,
    SchoolSerializer
)


class LeagueViewSet(BaseViewSet):
    queryset_school = School.objects.filter(active=True)
    serializer_class = LeagueSerializer
    province_id = 0
    county_id = 0

    # @app_enable(PartProject.league_school_show)
    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = OtherSchoolSerializer
        instance = self.queryset_school.filter(
            id=kwargs.get("pk", 0),
        )
        if instance.exists():
            serializer = self.get_serializer(instance.get())
            data = serializer.data
            self.add_count_ranking(data, instance.get())
            return Response(data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def add_count_ranking(self, data, school):
        data["rank_from_nationality"] = self.queryset_school.filter(gender=school.gender).count()
        data["rank_from_province"] = self.queryset_school.filter(
            gender=school.gender,
            province_id=school.province_id
        ).count()

        data["rank_from_county"] = self.queryset_school.filter(
            county_id=school.county_id,
            gender=school.gender,
        ).count()

    def list(self, request, *args, **kwargs):
        user_type = get_user_type(request.user)
        list_tab = [{}]
        if user_type == "student":
            type_query = request.query_params.get("query_type", None)

            if type_query == "top_school":
                return self.get_top_school(request)

            elif type_query == "citizen":
                return self.get_citizen_school(request, user_type)

            elif type_query == "provincial":
                return self.get_provincial_school(request, user_type)

            elif type_query == "same_point":
                return self.get_same_point_school(request)

            else:
                student = Student.objects.filter(id=request.user.id).select_related('school').get()
                list_tab = copy.deepcopy(list_column_league_student)
                # for item in list_tab:
                #     if item["query_type"] == "citizen" and student.school.point > MIN_POINT_CITIZEN:
                #         item["locked"] = False
                #         continue
                #
                #     if item["query_type"] == "provincial" and student.school.point > MIN_POINT_PROVINCIAL:
                #         item["locked"] = False
                #         continue

                response = {
                    "results": list_tab,
                    "rank": student.school.rank,
                    "point": student.school.point
                }
                return Response(response)

        elif user_type == "teacher":
            # متناسب با نقش در لیگ تب ها را نشان می دهیم

            # if has_perm_both_gender(request.user):
            #     gender = "both"
            # else:
            #     gender = request.user.baseuser.gender
            role = request.GET.get('role', [])
            gender = request.GET.get('gender', False)
            camp_id, county_id, province_id = get_user_location_role(request.user, role)
            if role in ["county", "camp", "coach"]:
                list_tab = copy.deepcopy(list_column_league_teacher)
            elif role in ["province", "province_f", "province_m"]:
                list_tab = copy.deepcopy(list_column_league_province)
            elif role == "country":
                list_tab = copy.deepcopy(list_column_league_country)
            else:
                list_tab = copy.deepcopy(list_column_league_country)

            type_query = request.query_params.get("query_type", None)

            if type_query == "top_school":
                return self.get_top_school(request)

            elif type_query == "citizen":
                # return self.get_citizen_school(request, user_type)
                return self.get_citizen_school_with_county_id(county_id, gender)

            elif type_query == "provincial":
                return self.get_provincial_school_with_province_id(province_id, gender)

            else:
                response = {
                    "results": list_tab,
                    "rank": 0,
                    "point": 0
                }
                return Response(response)

    # @app_enable(PartProject.league_top_school)
    # @method_decorator(cache_page(60 * 60 * 6))
    def get_top_school(self, request):
        has_perm = has_perm_both_gender(request.user)
        if has_perm:
            gender = GENDER.get(request.query_params.get('gender', request.user.baseuser.gender), request.user.baseuser.gender)
        else:
            gender = request.user.baseuser.gender

        queryset = self.queryset_school.filter(~Q(point=0), gender=gender, rank__lte=50).order_by('rank')
        serializer = self.get_serializer(queryset, many=True)
        response = {
            "results": serializer.data,
            "count": queryset.count()
        }
        return Response(response)

    # @app_enable(PartProject.league_citizen_school)
    def get_citizen_school(self, request, user_type):
        if user_type == "student":
            student = Student.objects.filter(id=request.user.id).select_related('school').get()
            county_id = student.school.county_id
            if student.school.point > MIN_POINT_CITIZEN:
                queryset = self.queryset_school.filter(
                    gender=request.user.baseuser.gender,
                    county_id=county_id
                ).order_by('rank')[0:20]

                serializer = self.get_serializer(queryset, many=True)
                response = {
                    "results": serializer.data,
                    "count": queryset.count()
                }
                return Response(response)
            return Response(status=status.HTTP_403_FORBIDDEN)

        elif user_type == "teacher":
            try:
                county_id = self.queryset_school.filter(
                    teacher_id=request.user.id
                )[0].county_id
            except:
                response = {
                    "results": [],
                    "count": 0
                }
                return Response(response)

            queryset = self.queryset_school.filter(
                gender=request.user.baseuser.gender,
                county_id=county_id
            ).order_by('rank')[0:20]

            serializer = self.get_serializer(queryset, many=True)
            response = {
                "results": serializer.data,
                "count": queryset.count()
            }
            return Response(response)

        return Response(status=status.HTTP_404_NOT_FOUND)

    # @app_enable(PartProject.league_provincial_school)
    def get_provincial_school(self, request, user_type):
        if user_type == "student":
            student = Student.objects.filter(id=request.user.id).select_related('school').get()
            if student.school.point > MIN_POINT_PROVINCIAL:
                province_id = student.school.province_id

                queryset = self.queryset_school.filter(
                    gender=request.user.baseuser.gender,
                    province_id=province_id
                ).order_by('rank')[0:20]

                serializer = self.get_serializer(queryset, many=True)
                response = {
                    "results": serializer.data,
                    "count": queryset.count()
                }
                return Response(response)

            return Response(status=status.HTTP_403_FORBIDDEN)

        # elif user_type == "teacher":
        #
        #     try:
        #         if role == "coach":
        #             province_id = self.queryset_school.filter(teacher_id=request.user.id)[0].province_id
        #         elif role in ["province", "province_f", "province_m"]:
        #             province_id = self.queryset_province.filter(coaches__in=[request.user.id])[0].province_id
        #
        #     except:
        #         response = {
        #             "results": [],
        #             "count": 0
        #         }
        #         return Response(response)
        #
        #     queryset = self.queryset_school.filter(
        #         gender=request.user.baseuser.gender,
        #         province_id=province_id
        #     ).order_by('rank')[0:20]
        #
        #     serializer = self.get_serializer(queryset, many=True)
        #     response = {
        #         "results": serializer.data,
        #         "count": queryset.count()
        #     }
        #     return Response(response)

        return Response(status=status.HTTP_404_NOT_FOUND)

    def get_provincial_school_with_province_id(self, province_id, gender):
        try:
            if gender == "both":
                queryset = self.queryset_school.filter(
                    province_id=province_id
                ).order_by('rank')[0:20]
            else:
                queryset = self.queryset_school.filter(
                    gender=gender,
                    province_id=province_id
                ).order_by('rank')[0:20]

            serializer = self.get_serializer(queryset, many=True)
            response = {
                "results": serializer.data,
                "count": queryset.count()
            }
            return Response(response)
        except:
            response = {
                "results": [],
                "count": 0
            }
            return Response(response)

    def get_citizen_school_with_county_id(self, county_id, gender):
        try:
            if gender == "both":
                queryset = self.queryset_school.filter(
                    county_id=county_id
                ).order_by('rank')[0:20]
            else:
                queryset = self.queryset_school.filter(
                    gender=gender,
                    county_id=county_id
                ).order_by('rank')[0:20]

            serializer = self.get_serializer(queryset, many=True)
            response = {
                "results": serializer.data,
                "count": queryset.count()
            }
            return Response(response)
        except:
            response = {
                "results": [],
                "count": 0
            }
            return Response(response)

    # @app_enable(PartProject.league_same_point_school)
    def get_same_point_school(self, request):
        student = Student.objects.filter(id=request.user.id).select_related('school')
        if student:
            student = student.get()
            point = student.school.point

            queryset = self.queryset_school.filter(
                gender=request.user.baseuser.gender,
                point__range=(point - MIN_SAME_POINT, point + MAX_SAME_POINT)
            ).order_by('rank')[0:20]

            serializer = self.get_serializer(queryset, many=True)
            response = {
                "results": serializer.data,
                "count": queryset.count()
            }
            return Response(response)
        return Response(status=status.HTTP_404_NOT_FOUND)


class ProvinceViewSet(BaseViewSet):
    queryset = Province.objects.all().exclude(code='123456789').order_by('title')
    serializer_class = ProvinceSerializer
    pagination_class = LargeResultsSetPagination

    @detail_route(methods=['get'], url_path='cities')
    def get_province_cities(self, request, pk=None):
        self.serializer_class = CountySerializer

        cities = County.objects.filter(province=pk)

        serializer = self.get_serializer(cities, many=True)
        serialized_data = serializer.data
        return Response(serialized_data)


class CountyViewSet(BaseViewSet):
    queryset = County.objects.all().order_by('title')
    serializer_class = CountySerializer
    pagination_class = LargeResultsSetPagination

    @detail_route(methods=['get'], url_path='camps')
    def get_province_cities(self, request, pk=None):
        self.serializer_class = CampSerializer
        camps = Camp.objects.filter(county=pk)

        serializer = self.get_serializer(camps, many=True)
        serialized_data = serializer.data
        return Response(serialized_data)

    def list(self, request, *args, **kwargs):
        county = County.objects.filter(province__coaches__id=request.user.id)

        serializer = self.get_serializer(county, many=True)
        serialized_data = serializer.data
        return Response(serialized_data)


class CampViewSet(BaseViewSet):
    queryset = Camp.objects.all()
    serializer_class = CampSerializer
    pagination_class = LargeResultsSetPagination

    @detail_route(methods=['get'], url_path='schools')
    def get_camp_schools(self, request, pk=None):
        self.serializer_class = SchoolSerializer
        schools = School.objects.filter(camp_id=pk)

        serializer = self.get_serializer(schools, many=True)
        serialized_data = serializer.data
        return Response(serialized_data)

    def list(self, request, *args, **kwargs):
        camps = Camp.objects.filter(county__coach__id=request.user.id)

        serializer = self.get_serializer(camps, many=True)
        serialized_data = serializer.data
        return Response(serialized_data)


class TeacherSchool(BaseViewSet):
    queryset = School.objects.filter(active=True)
    serializer_class = SchoolTeacherSerializer

    def list(self, request, *args, **kwargs):
        level = request.GET.get('role', False)
        has_perm = has_perm_both_gender(request.user)
        q_object = Q()

        if has_perm:
            gender = GENDER.get(request.query_params.get('gender', request.user.baseuser.gender), request.user.baseuser.gender)
        else:
            gender = request.user.baseuser.gender

        if level == "camp":
            camp = Camp.objects.filter(coach_id=request.user.id)
            if camp.exists():
                camp = camp[0].id

                q_object.add(Q(camp_id=camp), Q.AND)

        elif level == "county":
            county = County.objects.filter(coach_id=request.user.id)
            if county.exists():
                county_id = county[0].id
                q_object.add(Q(county_id=county_id), Q.AND)

            camp = request.GET.get('camp')
            if camp:
                if camp == "without_camp":
                    q_object.add(Q(camp_id=None), Q.AND)
                else:
                    q_object.add(Q(camp_id=camp), Q.AND)

        elif level == "province" or level == "province_f" or level == "province_m":
            province = Province.objects.filter(coaches__id=request.user.id)
            if province.exists():
                province = province[0].id
                q_object.add(Q(province_id=province), Q.AND)
            else:
                q_object.add(Q(province_id=0), Q.AND)

            county = request.GET.get('county')
            if county:
                q_object.add(Q(county_id=county), Q.AND)

            camp = request.GET.get('camp')
            if camp:
                if camp == "without_camp":
                    q_object.add(Q(camp_id=None), Q.AND)
                else:
                    q_object.add(Q(camp_id=camp), Q.AND)

        elif level == "country":
            province = request.GET.get('province')
            if province:
                q_object.add(Q(province_id=province), Q.AND)

            county = request.GET.get('county')
            if county:
                q_object.add(Q(county_id=county), Q.AND)

            camp = request.GET.get('camp')
            if camp:
                if camp == "without_camp":
                    q_object.add(Q(camp_id=None), Q.AND)
                else:
                    q_object.add(Q(camp_id=camp), Q.AND)

        else:
            q_object.add(Q(teacher_id=request.user.id), Q.AND)

        if len(q_object.children) > 0 or level == "country":
            queryset = self.queryset.filter(
                q_object,
            ).order_by('rank')

            queryset = queryset.filter(gender=gender)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return Response({
                "count": 0,
                "next": None,
                "previous": None,
                "results": [],
            }, status=status.HTTP_200_OK)
