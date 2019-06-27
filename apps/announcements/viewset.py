import json
import datetime
from cerberus import Validator
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from django.db.models import Q
from django.db import transaction
from apps.announcements.schema import announcements_schema, update_announcements_schema
from dashboard.logger import logger_api
from dashboard.settings.base import CACHE_TIME_ANN_COUNT
from utils.user_type import get_user_type, get_user_level
from apps.announcements.models import AnnouncementReceiver, Announcement, AnnouncementSeenHistory, AnnouncementFile
from apps.common.viewsets import BaseViewSet, BaseViewSetReadOnly
from apps.user.models.student import Student
from apps.league.models import School, Province, County
from apps.announcements.serializer import (
    AnnouncementSerializer,
    DetailAnnouncementReceiverSerializer
)


class MyAnnouncementViewSet(BaseViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

    def list(self, request, *args, **kwargs):
        user_type = get_user_type(request.user)

        if user_type == 'teacher':
            queryset = self.get_queryset().filter(creator_id=request.user.id).order_by('-created_at')
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
                return response

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        else:
            return Response([])


class AnnouncementCountViewSet(BaseViewSetReadOnly):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

    def list(self, request, *args, **kwargs):
        try:
            cache_key = 'announcement_count_{0}'.format(request.user.id)
            data = cache.get(cache_key)
            if data:
                if AnnouncementViewSet.near_next_announcement_date and datetime.datetime.now() >= AnnouncementViewSet.near_next_announcement_date:
                    """ اگر زمان انتشار نزدیک ترین اطلاعیه ای که در آینده باید  منتشر شده بود رسیده 
                     و نزدیکترین زمان انتشاراطلاعیه بعدی تغییر کند
                     یعنی تعداد  اطلاعیه در کش معتبر نیست و باید مجددا حساب شود 
                     """
                    AnnouncementViewSet.near_next_announcement_date = get_near_next_announcement_publish_date()
                    AnnouncementViewSet.last_announcement_date = get_last_announcement_publish_date()
                elif data['date_calculate'] >= AnnouncementViewSet.last_announcement_date:
                    """ 
                    تاریخ ساخته شدن کش بزرگتر از  تاریخ انتشار اخرین اطلاعیه باشد
                    یعنی تعداد اطلاعیه ها در کش معتبر است 
                    """
                    # logger_api.info("AnnouncementCount memcache", extra={
                    #     "detail": {
                    #         "user": request.user.id,
                    #     }
                    # })
                    data = {"count": data['count']}
                    return Response(data)
                else:
                    """ در این حالت اطلاعیه جدید منتشر شده و باید تعداد اطلاعیه مجددا محاسبه شود"""
                    pass
        except Exception as e:
            logger_api.error("AnnouncementCount  get cache  Error", extra={
                "detail": {
                    "error": e,
                }
            })
        # logger_api.error("AnnouncementCount calculate", extra={"detail": {"user": request.user.id, }})
        count = self.calculate_announcement_count(request)
        data = {"count": count, "date_calculate": datetime.datetime.now()}
        cache.set(cache_key, data, CACHE_TIME_ANN_COUNT)
        data = {"count": data['count']}
        return Response(data)

    def calculate_announcement_count(self, request):
        """ تابع محاسبه تعداد اطلاعیه های خوانده نشده یک کاربر"""
        # kahrizi
        count = 0
        try:
            cache_key = 'announcement_count_{0}'.format(request.user.id)
            announcement_view = AnnouncementSeenHistory.objects.filter(user_id=request.user.id).count()

            user_type = get_user_type(request.user)

            if user_type == 'student':
                announcement_not_view = get_queryset_for_student(request_data=request).count()

            elif user_type == 'teacher':
                announcement_not_view = get_queryset_for_teacher(request_data=request)
                announcement_ids = set(list(announcement_not_view.values_list("announcement_id", flat=True)))
                announcement_not_view = self.get_queryset().filter(id__in=announcement_ids).count()
            else:
                count = 0
                return count

            count = announcement_not_view - announcement_view

            if count < 0:
                count = 0
                # logger_api.error("AnnouncementCount  calculate_announcement_count Error", extra={
                #     "detail": {
                #         "error": "AnnouncementCount =" + str(count) + "User=" + str(request.user.id),
                #     }
                # })

        except Exception as e:
            logger_api.error("AnnouncementCount  calculate_announcement_count Error", extra={
                "detail": {
                    "error": e,
                }
            })

        finally:
            data = {"count": count, "date_calculate": datetime.datetime.now()}
            cache.set(cache_key, data, CACHE_TIME_ANN_COUNT)
            return count


def get_last_announcement_publish_date():
    """برای محاسبه تاریخ آخرین اطلاعیه منتشر شده"""
    # kahrizi
    last_announcement_publish_date = None
    try:
        queryset = Announcement.objects.filter(release_time__lte=datetime.datetime.now()).order_by('-release_time').values('release_time')
        last_announcement_publish_date = queryset[0]['release_time']
        queryset = Announcement.objects.filter(created_at__lte=datetime.datetime.now()).order_by('-created_at').values('created_at')
        created_at = queryset[0]['created_at']
        if created_at > last_announcement_publish_date:
            last_announcement_publish_date = created_at

        return last_announcement_publish_date
    except Exception as ex:
        return last_announcement_publish_date


def get_near_next_announcement_publish_date():
    """برای محاسبه تاریخ نزدیکترین  اطلاعیه ای که در آینده منتشر می شود"""
    # kahrizi
    near_next_announcement_date = None
    try:
        queryset = Announcement.objects.filter(release_time__gt=datetime.datetime.now()).order_by('release_time').values('release_time')
        near_next_announcement_date = queryset[0]['release_time']
        return near_next_announcement_date
    except Exception as ex:
        return near_next_announcement_date


class AnnouncementViewSet(BaseViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    last_announcement_date = get_last_announcement_publish_date()
    near_next_announcement_date = get_near_next_announcement_publish_date()

    def list(self, request, *args, **kwargs):
        user_type = get_user_type(request.user)

        if user_type == 'student':
            _query_set = get_queryset_for_student(request_data=request)

        elif user_type == 'teacher':
            _query_set = get_queryset_for_teacher(request_data=request)

        else:
            return Response([])

        if _query_set is None:
            return Response([])

        announcement_ids = set(list(_query_set.values_list("announcement_id", flat=True)))
        _main_query = Q()
        _main_query.add(Q(id__in=announcement_ids), Q.AND)

        queryset = self.get_queryset().filter(_main_query).order_by('-created_at')
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            return response

        serializer = self.get_serializer(_query_set, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # management view for announcement
        try:
            # announcement_visit = AnnouncementVisit(user_id=request.user.id, announcement=instance)
            # announcement_visit.save()

            instance.view_count = instance.view_count + 1
            instance.save()


        except:
            pass

        return Response(serializer.data)

    @detail_route(url_path='information', methods=['get'])
    def announcement_information(self, request, pk=None):
        instance = self.queryset.filter(id=pk)
        if not instance:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        instance = instance.get()
        serializer = self.get_serializer(instance)
        announcement = serializer.data

        # get all receiver for one announcement
        announcement_receivers = instance.announcement_receivers.all()
        serializer = DetailAnnouncementReceiverSerializer(announcement_receivers, many=True)
        announcement_receivers = serializer.data

        data = {"announcement": announcement, "announcement_receivers": announcement_receivers}
        return Response(data)

    @detail_route(url_path='delete_an', methods=['post'])
    def delete_announcement(self, request, pk=None):
        # check for exist
        announcement = Announcement.objects.filter(id=pk)
        if not announcement:
            serializer = {
                'message ': 'announcement not found or you are not permission to delete announcement'
            }
            return Response(serializer, status=status.HTTP_404_NOT_FOUND)

        # check for permission edit for this user
        announcement = announcement.filter(creator_id=request.user.id)
        if not announcement:
            return Response(status=status.HTTP_403_FORBIDDEN)

        announcement.delete()
        AnnouncementViewSet.last_announcement_date = get_last_announcement_publish_date()
        AnnouncementViewSet.near_next_announcement_date = get_near_next_announcement_publish_date()
        return Response(status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):

        # custom parameters
        post_req = self.cleaned_data(request=request)

        # validate data enter
        v = Validator(announcements_schema())
        v.allow_unknown = True
        if not v.validate(post_req):
            return Response({"message": v.errors}, status=status.HTTP_400_BAD_REQUEST)

        # add announcement
        announcement = Announcement(
            title=post_req['title'],
            description=post_req['description'],
            date=post_req['date'] if post_req.get('date', None) else datetime.datetime.now(),
            release_time=post_req['release_time'] if post_req.get('release_time', None) else datetime.datetime.now(),
            has_date=post_req.get('has_date', False),
            image=request.data.get('image') if request.data.get('image') else "",
            creator_id=self.request.user.id
        )
        announcement.save()
        AnnouncementViewSet.last_announcement_date = get_last_announcement_publish_date()
        AnnouncementViewSet.near_next_announcement_date = get_near_next_announcement_publish_date()
        # add files for announcement
        self.save_file(announcement, request)

        # add announcement receiver
        self.add_announcement_receiver(announcement, post_req)
        return Response(status=status.HTTP_201_CREATED)

    @detail_route(url_path='update', methods=['post'])
    def update_announcement(self, request, pk=None):
        # check for exist
        announcement = Announcement.objects.filter(id=pk)
        if not announcement:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # check for permission edit for this user
        announcement = announcement.filter(creator_id=request.user.id)
        if not announcement:
            return Response(status=status.HTTP_403_FORBIDDEN)

        announcement = announcement.prefetch_related("announcement_receivers")

        # custom parameters
        post_req = self.cleaned_data(request=request)

        # validate data enter
        v = Validator(update_announcements_schema())
        v.allow_unknown = True
        if not v.validate(post_req):
            return Response({"message": v.errors}, status=status.HTTP_400_BAD_REQUEST)

        # validate management announcement receiver
        pre_announcement_receiver = announcement.get().announcement_receivers.all().count()
        new_announcement_receiver = len(post_req['receivers'])
        deleted_announcement_receiver = len(post_req['deleted_receivers'])

        if deleted_announcement_receiver >= pre_announcement_receiver + new_announcement_receiver:
            return Response({"receivers": "Required receivers"}, status.HTTP_400_BAD_REQUEST)

        # update announcement
        announcement_item = dict(
            title=post_req['title'],
            description=post_req['description'],
            date=post_req.get('date', None),
            release_time=post_req.get('release_time', None),
            has_date=post_req.get('has_date', False),
            creator_id=self.request.user.id
        )

        if request.data.get("deleted_image", None) == "yes":
            announcement_item['image'] = ""

        announcement.update(**announcement_item)

        announcement = announcement.get()

        if request.data.get('image'):
            announcement.image = request.data.get('image')
            announcement.save()

        # delete files from announcement
        self.delete_files(post_req, announcement_id=announcement.id)

        # add files for announcement
        self.save_file(announcement, request)

        # add announcement receiver
        self.add_announcement_receiver(announcement, post_req)

        # delete announcement receiver for announcement
        self.delete_announcement_receiver(post_req, announcement_id=announcement.id)

        AnnouncementViewSet.last_announcement_date = get_last_announcement_publish_date()
        AnnouncementViewSet.near_next_announcement_date = get_near_next_announcement_publish_date()
        return Response(status=status.HTTP_200_OK)

    def add_announcement_receiver(self, announcement, post_req):

        """
        :param announcement: 
        :param post_req: 
        :return: 
        """
        # list announcement receiver for add later
        # try:
        announcement_receiver_list = []

        user_levels = get_user_level(user=self.request.user)

        for receiver in post_req['receivers']:

            announcement_receiver = dict(
                user_type=receiver['user_type'],
                announcement=announcement
            )

            if "country" in user_levels:
                announcement_receiver['province_id'] = receiver['province'] if receiver['province'] != 'all' else None
                announcement_receiver['county_id'] = receiver['county'] if receiver['county'] != 'all' else None
                announcement_receiver['camp_id'] = receiver['camp'] if receiver['camp'] != 'all' else None
                announcement_receiver['gender'] = receiver['gender']

            elif "province" in user_levels:
                announcement_receiver['province_id'] = Province.objects.get(coaches__id=self.request.user.id).id
                announcement_receiver['county_id'] = receiver['county'] if receiver['county'] != 'all' else None
                announcement_receiver['camp_id'] = receiver['camp'] if receiver['camp'] != 'all' else None
                announcement_receiver['gender'] = receiver['gender']

            elif "province_f" in user_levels:
                announcement_receiver['province_id'] = Province.objects.get(coaches__id=self.request.user.id).id
                announcement_receiver['gender'] = "female"
                announcement_receiver['camp_id'] = receiver['camp'] if receiver['camp'] != 'all' else None
                announcement_receiver['county_id'] = receiver['county'] if receiver['county'] != 'all' else None

            elif "province_m" in user_levels:
                announcement_receiver['province_id'] = Province.objects.get(coaches__id=self.request.user.id).id
                announcement_receiver['gender'] = "male"
                announcement_receiver['camp_id'] = receiver['camp'] if receiver['camp'] != 'all' else None
                announcement_receiver['county_id'] = receiver['county'] if receiver['county'] != 'all' else None

            elif "county" in user_levels:
                # announcement_receiver['province_id'] = Province.objects.get(coaches__id=self.request.user.id).id
                announcement_receiver['county_id'] = County.objects.get(coach__id=self.request.user.id).id
                announcement_receiver['camp_id'] = receiver['camp'] if receiver['camp'] != 'all' else None
                announcement_receiver['gender'] = receiver['gender']

            announcement_receiver_list.append(AnnouncementReceiver(**announcement_receiver))

        AnnouncementReceiver.objects.bulk_create(announcement_receiver_list)
        # except Exception as ex:
        #     pass

    @staticmethod
    def delete_announcement_receiver(post_req, announcement_id):

        AnnouncementReceiver.objects.filter(
            id__in=post_req['deleted_receivers'],
            announcement_id=announcement_id
        ).delete()
        return True

    def save_file(self, announcement, request):
        for file in self.request.data.getlist("files[]"):
            file_model = AnnouncementFile()
            file_model.file = file
            file_model.announcement = announcement
            file_model.save()

    @staticmethod
    def delete_files(post_req, announcement_id):
        AnnouncementFile.objects.filter(id__in=post_req['deleted_files'], announcement_id=announcement_id).delete()

    @staticmethod
    def cleaned_data(request):
        post_req = {
            "title": request.POST.get("title", ""),
            "description": request.POST.get("description", ""),
            "has_date": request.POST.get("has_date", ""),
            "date": request.POST.get("release_time", ""),
            "release_time": request.POST.get("release_time", ""),
            "deleted_image": request.POST.get("deleted_image", ""),
            "receivers": json.loads(request.POST.get("receivers", '[]')),
            "deleted_receivers": json.loads(request.POST.get("deleted_receivers", '[]')),
            "deleted_files": json.loads(request.POST.get("deleted_files", '[]')),
        }
        for field in list(post_req):
            if post_req[field] == "":
                post_req.pop(field)

        return post_req

    @detail_route(url_path='seen', methods=['get'])
    def announcement_seen(self, request, pk=None):

        user = request.user
        try:
            ac = AnnouncementSeenHistory()
            ac.announcement_id = pk
            ac.user = user
            ac.save()

            announcement_count = AnnouncementCountViewSet()
            announcement_count.calculate_announcement_count(request)

            # cache_key = 'announcement_count_{0}'.format(request.user.id)  # needs to be unique
            # data = cache.get(cache_key)  # returns None if no key-value pair
            # if data:
            #     data = {"count": data.get("count", 1) - 1}
            #     cache.set(cache_key, data, settings.CACHESANNCOUNT)

            return Response({
                "status": "success",
                "message": ""
            })

        except Announcement.DoesNotExist:

            return Response({
                "status": "error",
                "message": "announcement does not exist"
            })


def get_queryset_for_student(request_data, has_date=None, start_date=None, end_date=None):
    student = Student.objects.filter(id=request_data.user.id).select_related("school")
    if not student.exists():
        return None

    student = student.get()
    query_announcement_object = Q()
    query_announcement_object.add(Q(school=student.school) | Q(school=None), Q.AND)
    query_announcement_object.add(Q(county_id=student.school.county_id) | Q(county_id=None), Q.AND)
    query_announcement_object.add(Q(province_id=student.school.province_id) | Q(province_id=None), Q.AND)
    query_announcement_object.add(Q(camp_id=student.school.camp_id) | Q(camp_id=None), Q.AND)
    query_announcement_object.add(Q(user_type="student") | Q(user_type=None), Q.AND)
    query_announcement_object.add(Q(gender__in=[student.gender, 'both']), Q.AND)

    query_announcement_object.add(Q(announcement__release_time__lte=datetime.datetime.now()), Q.AND)
    if has_date:
        query_announcement_object.add(Q(announcement__has_date=True), Q.AND)

    if start_date:
        query_announcement_object.add(Q(announcement__date__gte=start_date), Q.AND)

    if end_date:
        query_announcement_object.add(Q(announcement__date__lte=end_date), Q.AND)

    queryset = AnnouncementReceiver.objects.filter(query_announcement_object)
    return queryset.order_by('-created_at')


def get_queryset_for_teacher(request_data, has_date=None, start_date=None, end_date=None):
    list_user_levels = get_user_level(user=request_data.user, user_type='teacher')

    query_announcement_object = Q()
    query_announcement_object.add(Q(user_type__in=list_user_levels), Q.AND)

    levels = ['coach', 'camp', 'county', 'province']
    # user have any levels from list top call def
    if any(element in levels for element in list_user_levels):
        query_announcement_by_schools(list_user_levels, query_announcement_object, request_data)

    query_announcement_object.add(Q(announcement__release_time__lte=datetime.datetime.now()), Q.AND)
    if has_date:
        query_announcement_object.add(Q(announcement__has_date=True), Q.AND)

    if start_date:
        query_announcement_object.add(Q(announcement__date__gte=start_date), Q.AND)

    if end_date:
        query_announcement_object.add(Q(announcement__date__lte=end_date), Q.AND)

    queryset = AnnouncementReceiver.objects.filter(query_announcement_object)
    return queryset.order_by('-created_at')


def query_announcement_by_schools(list_user_type, query_announcement_object, request_data):
    list_county = []
    list_province = []
    list_camp = []
    list_school = []
    query_school_object = Q()

    if 'coach' in list_user_type:
        query_school_object.add(Q(teacher_id=request_data.user.id), Q.OR)
    if 'camp' in list_user_type:
        query_school_object.add(Q(camp__coach_id=request_data.user.id), Q.OR)
    if 'county' in list_user_type:
        query_school_object.add(Q(county__coach_id=request_data.user.id), Q.OR)
    if 'province' in list_user_type:
        query_school_object.add(Q(province__coaches__in=[request_data.user]), Q.OR)

    schools = School.objects.filter(query_school_object)
    for school in schools:
        list_school.append(school.id)
        list_county.append(school.county_id)
        list_province.append(school.province_id)
        list_camp.append(school.camp_id)

    query_announcement_object.add(Q(Q(school_id__in=list(set(list_school))) | Q(school_id=None)), Q.AND)
    query_announcement_object.add(Q(Q(county_id__in=list(set(list_county))) | Q(county_id=None)), Q.AND)
    query_announcement_object.add(Q(Q(province_id__in=list(set(list_province))) | Q(province_id=None)), Q.AND)
    query_announcement_object.add(Q(Q(camp_id__in=list(set(list_camp))) | Q(camp_id=None)), Q.AND)
    query_announcement_object.add(Q(gender__in=[request_data.user.baseuser.gender, 'both']), Q.AND)
