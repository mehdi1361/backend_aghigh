from django import template
from apps.notification.models import Notification

register = template.Library()


@register.filter
def get_notifications(user):
    notification_model = Notification.objects.filter(send_to_id=user.id, seen=False).all()
    return notification_model


@register.filter
def get_notifications_count(user):
    return Notification.objects.filter(send_to_id=user.id, seen=False).count()
