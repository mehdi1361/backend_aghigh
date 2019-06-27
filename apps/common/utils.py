import os
import jdatetime
from enum import Enum, unique


@unique
class PartProject(Enum):
    # کلاس بخش های مختلف پروژه برای پاس دادن به تابع زیر و برای خوانایی بیشتر کدهای برنامه

    activity = 1000,
    activity_show = 1001,
    activity_create = 1002,
    activity_star = 1003,
    activity_comment = 1004,
    activity_search = 1005,
    activity_rate_users = 1006,
    activity_check = 1007,
    activity_update = 1008,

    question = 2000,
    question_create = 2001,
    question_answer = 2002,
    question_search = 2003,
    question_score = 2004,

    shop = 3000,
    shop_buy = 3001,
    shop_search = 3002,
    shop_create = 3003,

    schedule = 4000,
    schedule_add = 4001,
    schedule_del = 4002,
    schedule_announcements = 4003,
    schedule_search = 4004,

    league = 5000,
    league_search = 5001,
    # league_search = 5001,

    report = 7000,

    emtiaz = 8000,
    emtiaz_search = 8001,

    announcement = 9000,
    announcement_read = 9001,

    notification = 10000,


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def remove_file(path):
    os.remove(path)


def to_jorjean(miladi_date):
    date_time = miladi_date.split(' ')
    result_date = date_time[0].split('-')
    result_date = jdatetime.GregorianToJalali(int(result_date[0]), int(result_date[1]), int(result_date[2]))
    result_date = str(result_date.jyear) + "-" + add_zero(str(result_date.jmonth)) + "-" + add_zero(str(result_date.jday))
    return result_date + "T" + date_time[1][0:8]


def gregorian_to_persian(miladi_date, str_type="%a %d %b %Y"):
    return jdatetime.datetime.fromgregorian(datetime=miladi_date).strftime(str_type)


def gregorian_to_persian_chart(miladi_date, str_type="%Y/%m/%d"):
    return jdatetime.datetime.fromgregorian(datetime=miladi_date).strftime(str_type)


def add_zero(value):
    if len(value) == 1:
        return "0" + value
    return value
