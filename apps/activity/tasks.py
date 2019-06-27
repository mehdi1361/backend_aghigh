from celery import shared_task
from datetime import datetime, timedelta

from apps.activity.models import Activity


@shared_task
def add_unchecked_activities_into_league():

    three_day_in_past = datetime.now() - timedelta(days=3)

    activities = Activity.objects.filter(created_at=three_day_in_past, state='NEW')
    if activities.exists():
        for activity in activities:
            if activity.state == 'NEW':
                activity.state = 'TIL'
                activity.accepted_at = datetime.now()
                activity.save()


@shared_task
def remove_unchecked_activities_from_league():
    activities = Activity.objects.filter(state='TIL')
    if activities.exists():
        for activity in activities:
            activity.state = 'REMOVE'
            activity.save()

