from django import template
from django.contrib.auth.models import User

register = template.Library()


@register.filter
def get_user_count(value):
    count = User.objects.all().count()
    return count
