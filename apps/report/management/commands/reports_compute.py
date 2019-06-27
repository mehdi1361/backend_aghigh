from django.core.management.base import BaseCommand
from apps.activity.models import Activity
from apps.report.models import Reports
from django.db.models import Avg, Count, F, Q
import datetime
from dashboard.mongo_db import cursor


class Command(BaseCommand):
    def handle(self, *args, **options):

        self.stdout.write(self.style.SUCCESS('Start compute reports'))

        activities_info = count_activity()

        Reports(
            view_count=users_view_count(),
            activity_count=activities_info['activity_count'],
            accept_avg=activities_info['average_difference'],
            school_count=school_count()
        ).save()

        self.stdout.write(self.style.SUCCESS('end compute reports'))


def count_activity():
    result = Activity.objects.filter(state="ACCEPT").aggregate(
        Count('id'),
        average_difference=Avg(F('accepted_at') - F('created_at'))
    )
    average_difference = round(
        result["average_difference"].days + (result["average_difference"].seconds / 3600 / 24), 2
    ) if result["average_difference"] is not None else 0

    return {'average_difference': average_difference, 'activity_count': result["id__count"]}


def school_count():
    count = Activity.objects.filter(
        ~Q(school__province__code="123456789"),
        state="ACCEPT"
    ).values('school_id').distinct('school_id').count()
    return count


def users_view_count():
    today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
    query = cursor.rest_log.find({"requested_at": {"$lte": today_max, "$gte": today_min}}).distinct('user_id')

    return len(query)
