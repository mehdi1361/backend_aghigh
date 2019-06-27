from celery import shared_task
from apps.emtiaz.compute import ComputingPoint


@shared_task
def computing_point_activity(activity_id):
    ComputingPoint().activity_point(activity_id)
