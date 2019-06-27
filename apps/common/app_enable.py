# kahrizi


import json

from rest_framework import status

from apps.common.models import DisableManager
from utils.user_type import get_user_type, get_user_level
from rest_framework.exceptions import APIException


class PermissionLocked(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'HTTP_423_LOCKED'


class AppDisableList:
    app_list_disable = []

    @staticmethod
    def load_app_list():
        AppDisableList.app_list_disable = []
        with open('./static/DisableManager.json', encoding='utf-8') as data_file:
            data = json.loads(data_file.read())
            for item in data:
                item_obj = DisableManager(item['id_part'], item['name_part'], item['parent_id'], item['status'], item['status_current'], item['admin_access'], item['message_disable'], item['start_date_disable'], item['end_date_disable'], item['hidden'], item['color'], item['alpha'])
                AppDisableList.app_list_disable.append(item_obj)


def app_enable(part):
    """
    دکوراتوری  که بررسی می کند که آیا این بخش برنامه فعال است یا نه
    :param part: بخش برنامه که در کلاس زیر است
    util.PartProject
    :return: اگر فعال بود به
    """

    def _method_wrapper(function):
        def wrap(request, *args, **kwargs):
            disable = False
            message = ''
            for item in AppDisableList.app_list_disable:
                if item.id_part == part.value[0]:
                    if item.status_current:
                        message = item.message_disable
                        user_type = get_user_type(request.request._user)
                        user_level = get_user_level(request.request._user, user_type)
                        disable = check_admin_acees(item, user_type, user_level)
                    break

            if disable:
                raise PermissionLocked(detail=message)

            return function(request, *args, **kwargs)

        wrap.__doc__ = function.__doc__
        wrap.__name__ = function.__name__
        return wrap

    return _method_wrapper


def check_admin_acees(part_item, user_type, user_level):
    """
    برای بررسی اینکه ادمین دسترسی داشته باشد یا نه
    :param part_item:
    :param user_type:
    :param user_level:
    :return:
    """
    disable = True
    # اگر برنامه غیرفعال شده بود بررسی کنیم اپمین در این حالت اجازه دسترسی دارد یا نه
    if part_item.admin_access and disable:
        if user_type == 'advisor' or user_type == 'admin':
            disable = False
        elif 'country' in user_level:  # TODO بعدا سلکت رول را پاس بدهیم تا بشود بر اساس رولی که انتخاب شده تصمی گرفت که نشان بدهد یا نه
            disable = False

    return disable
