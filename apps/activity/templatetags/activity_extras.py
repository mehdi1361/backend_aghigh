from django import template
from apps.activity.models import Activity
from apps.user.models.teacher import Teacher
from apps.user.models.student import Student


register = template.Library()


def get_context(max_depth=4):
    import inspect
    stack = inspect.stack()[2:max_depth]
    context = {}
    for frame_info in stack:
        frame = frame_info[0]
        arg_info = inspect.getargvalues(frame)
        if 'context' in arg_info.locals:
            context = arg_info.locals['context']
            break
    return context


@register.filter
def get_activity_count(value):
    return Activity.objects.count()


@register.filter
def get_coach_count(value):
    return Teacher.objects.count()


@register.filter
def get_student_count(value):
    return Student.objects.count()
