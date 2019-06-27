import datetime
import random
import jdatetime
import copy

from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import list_route
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from utils.user_type import get_user_type
from apps.activity.models import Activity
from apps.announcements.viewset import get_queryset_for_student, get_queryset_for_teacher
from apps.common.utils import to_jorjean
from apps.common.viewsets import LargeResultsSetPagination, BaseViewSet
from apps.common.calverter import Calverter
from apps.schedule.models.events import Event, Occurrence
from apps.schedule.models.rules import Rule
from apps.schedule.serializers import AnnualEventsSerializer, EventSerializer, OccurrenceSerializer
from apps.schedule.models.annual import AnnualEvents


class AnnualEventsViewSet(BaseViewSet):
    queryset = AnnualEvents.objects.all()
    serializer_class = AnnualEventsSerializer
    pagination_class = LargeResultsSetPagination

    def list(self, request, *args, **kwargs):
        params = request.query_params
        date = params.get("date", False)

        if date:
            try:
                date = date.split(",")
                day = int(date[2])
                month = int(date[1])
                year = int(date[0])
            except:
                raise ValidationError({"message": "date not valid"}, code=status.HTTP_400_BAD_REQUEST)

        else:
            date = datetime.datetime.now()
            day = date.day
            month = date.month
            year = date.year

        try:
            hijri = jdatetime.datetime.fromgregorian(day=day, month=month, year=year)

            cal = Calverter()
            jd = cal.gregorian_to_jd(year, month, day)
            islamic_year, islamic_month, islamic_day = cal.jd_to_islamic(jd)

        except:
            raise ValidationError({"message": "date not valid"}, code=status.HTTP_400_BAD_REQUEST)

        queryset = self.queryset.filter(
            Q(date_type="ISLAMIC", day=islamic_day, month=islamic_month) |
            Q(date_type="HIJRI", day=hijri.day, month=hijri.month) |
            Q(date_type="AD", day=day, month=month)
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class EventViewSet(BaseViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def create(self, request, *args, **kwargs):
        data = copy.copy(request.data)
        data["creator"] = request.user.id
        rule = data.get("rule", False)

        if rule:
            try:
                data["rule"] = Rule.objects.get(frequency=rule).id
            except:
                raise ValidationError({"message": "rule not valid"}, code=status.HTTP_400_BAD_REQUEST)

        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if start_time and end_time:

            if not len(start_time.split(":")) == 2 and not len(end_time.split(":")) == 2:
                raise ValidationError(
                    {"message": "start_time or end_time has error"},
                    code=status.HTTP_400_BAD_REQUEST
                )

            data["all_day"] = False
            data["end"] = data["start"] + "T" + str(end_time)
            data["start"] = data["start"] + "T" + str(start_time)

        else:
            data["end"] = data["start"] + "T00:00"
            data["start"] = data["start"] + "T00:00"
            data["all_day"] = True

        if data.get('rule'):
            try:
                data["end_recurring_period"] = data["end_recurring_period"] + "T00:00"
            except:
                raise ValidationError(
                    {"message": "end_recurring_period is required"},
                    code=status.HTTP_400_BAD_REQUEST
                )

            week_days = data.get('week_days')
            if rule == "WEEKLY" and week_days:
                try:
                    data['by_week_day'] = ",".join([p for p in week_days])
                except:
                    raise ValidationError(
                        {"message": "week_day not valid"},
                        code=status.HTTP_400_BAD_REQUEST
                    )
        else:
            if 'end_recurring_period' in data:
                data.pop('end_recurring_period')

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()
        instance = serializer.instance
        if instance.end_recurring_period and instance.rule:
            year_recurring_period = instance.end_recurring_period.year
            year_now = datetime.datetime.now().year
            if year_now <= year_recurring_period < year_now + 1:
                occurrence_list = instance._get_occurrence_list(instance.start, instance.end_recurring_period)
                if len(occurrence_list) > 300:
                    raise ValidationError(
                        {"message": "you exceeded the limit."},
                        code=status.HTTP_400_BAD_REQUEST
                    )

                for occ in occurrence_list:
                    occ.save()
            else:
                raise ValidationError(
                    {"message": "you exceeded the limit."},
                    code=status.HTTP_400_BAD_REQUEST
                )

        else:
            occurrence = instance._create_occurrence(instance.start)
            occurrence.save()

    def list(self, request, *args, **kwargs):
        params = request.query_params
        end = params.get("end_date", "")
        start = params.get("start_date", "")
        user_type = get_user_type(request.user)

        try:
            start = datetime.datetime.strptime(start, '%Y-%m-%d')
            end = datetime.datetime.strptime(end, '%Y-%m-%d')

        except:
            raise ValidationError({"message": "start date or end date not valid"}, code=status.HTTP_400_BAD_REQUEST)

        response_data = []
        user = request.user

        self.get_occurrence(response_data, start, end, user)
        self.get_occurrence_announcements(response_data, start, end, request)

        if user_type == "student":
            self.get_occurrence_activities(response_data, start, end, user)

        return Response(response_data)

    @staticmethod
    def get_occurrence(response_data, start, end, user):
        occurrences = Occurrence.objects.filter(
            event__creator_id=user.id,
            start__lte=end,
            start__gte=start
        )

        for occurrence in occurrences:
            recur_rule = occurrence.event.rule.name \
                if occurrence.event.rule else None

            if occurrence.event.end_recurring_period:
                recur_period_end = occurrence.event.end_recurring_period
            else:
                recur_period_end = None

            event_start = occurrence.start
            event_end = occurrence.end

            if occurrence.cancelled:
                color = "#c7c7c7"
            else:
                color = occurrence.event.color_event

            response_data.append({
                'id': occurrence.id,
                'title': occurrence.title,
                'start': event_start,
                'start_jalali': to_jorjean(str(event_start)),
                'end': event_end,
                'event_id': occurrence.event.id,
                'color': color,
                'description': occurrence.description,
                'rule': recur_rule,
                'end_recurring_period': recur_period_end,
                'cancelled': occurrence.cancelled,
                'all_day': occurrence.all_day,
                'editable': True if not occurrence.cancelled else False,
                'type': "occurrence",
                'id_href': None,
            })

    @staticmethod
    def get_occurrence_activities(response_data, start, end, user):
        activities = Activity.objects.filter(
            student_id=user.id,
            start_date__lte=end,
            state__in=["ACCEPT", "TIL"],
            start_date__gte=start
        )
        color = "#6c4cc9"
        if user.baseuser.gender == "female":
            color = "#e645d0"

        for activity in activities:
            response_data.append({
                'id': random.randint(9999, 99999),
                'title': activity.title,
                'start': activity.start_date,
                'start_jalali': to_jorjean(str(activity.start_date)),
                'end': activity.end_date,
                'event_id': random.randint(9999, 99999),
                'color': color,
                'description': activity.description,
                'rule': None,
                'end_recurring_period': None,
                'cancelled': None,
                'all_day': True,
                'editable': False,
                'type': "activity",
                'id_href': activity.id,
            })

    @staticmethod
    def get_occurrence_announcements(response_data, start, end, request):
        user_type = get_user_type(request.user)
        announcements = []
        if user_type == 'student':
            announcements = list(
                get_queryset_for_student(request_data=request, has_date=True, start_date=start, end_date=end))

        elif user_type == 'teacher':
            announcements = list(
                get_queryset_for_teacher(request_data=request, has_date=True, start_date=start, end_date=end))

        for announcement in announcements:
            response_data.append({
                'id': random.randint(9999, 99999),
                'title': announcement.announcement.title,
                'start': announcement.announcement.date,
                'start_jalali': to_jorjean(str(announcement.announcement.date)),
                'end': None,
                'event_id': random.randint(9999, 99999),
                'color': "#00bbd2",
                'description': announcement.announcement.description,
                'rule': None,
                'end_recurring_period': None,
                'cancelled': None,
                'all_day': True,
                'editable': False,
                'type': "announcement",
                'id_href': announcement.announcement_id,
            })

    @list_route(url_path='delete', methods=['post'])
    def delete_event(self, request):
        params = request.data
        event_id = params.get("event_id", "")
        queryset = Event.objects.filter(id=event_id, creator_id=request.user.id)
        if queryset:
            queryset.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class OccurrenceViewSet(BaseViewSet):
    queryset = Occurrence.objects.all()
    serializer_class = OccurrenceSerializer

    def create(self, request, *args, **kwargs):
        pass

    def list(self, request, *args, **kwargs):
        pass

    @list_route(url_path='update', methods=['post'])
    def update_occurrence(self, request):
        data = request.data

        if data.get('device') != "android":
            return self.update_occurrence_web(data)
        return self.update_occurrence_mobile(data)

    def update_occurrence_web(self, data):
        data_update = {}

        try:
            start_date = data.get("start")
            if start_date:
                date = datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
                data_update["start"] = date
        except:
            pass

        try:
            end_date = data.get("end")
            if end_date:
                date = datetime.datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
                data_update["end"] = date
        except:
            pass

        all_day = data.get("all_day")
        if all_day is not None:
            if all_day:
                data_update["end"] = None

            data_update["all_day"] = all_day

        cancelled = data.get("cancelled")
        if cancelled is not None:
            data_update["cancelled"] = cancelled

        event_id = data.get("event_id")
        occurrence_id = data.get("occurrence_id")
        occurrence = Occurrence.objects.filter(id=occurrence_id, event__creator_id=self.request.user.id, event_id=event_id)
        if occurrence:
            occurrence.update(**data_update)
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND)

    def update_occurrence_mobile(self, data):
        action = data.pop("action")
        occurrence_id = data.get("id")
        data.pop("device")
        occurrence = Occurrence.objects.filter(id=occurrence_id, event__creator_id=self.request.user.id)
        if action == "delete":
            occurrence.delete()
            return Response(status=status.HTTP_200_OK)

        if action == "delete_all":
            Event.objects.filter(id=occurrence[0].event_id, creator_id=self.request.user.id).delete()
            return Response(status=status.HTTP_200_OK)

        elif action == "cancel":
            occurrence.update(cancelled=True)
            return Response(status=status.HTTP_200_OK)

        start_time = data.pop("start_time", None)
        end_time = data.pop("end_time", None)

        if start_time and end_time:

            if not len(start_time.split(":")) == 2 and not len(end_time.split(":")) == 2:
                raise ValidationError(
                    {"message": "start_time or end_time has error"},
                    code=status.HTTP_400_BAD_REQUEST
                )

            data["end"] = data["start"] + "T" + str(end_time)
            data["start"] = data["start"] + "T" + str(start_time)
            data["all_day"] = False

        else:
            data["end"] = data["start"] + "T00:00"
            data["start"] = data["start"] + "T00:00"
            data["all_day"] = True

        if occurrence:
            occurrence.update(**data)
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND)

    @list_route(url_path='delete', methods=['post'])
    def delete_occurrence(self, request):
        params = request.data
        occurrence_id = params.get("occurrence_id", "")
        queryset = Occurrence.objects.filter(id=occurrence_id, event__creator_id=request.user.id)
        if queryset:
            queryset.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
