import json
import time
import datetime
import threading

from django.db.models import Q
from apps.common.app_enable import AppDisableList
from apps.common.serializers import DisableManagerSerializer
from apps.common.models import DisableManager
from django.conf import settings


def make_json_disable_manager():
    """
    #تابعی برای ساخت فایل جیسون جدول وضعیت غیرفعال بودن بخش های مختلف برنامه
    """
    date = datetime.datetime.today()
    q_object = Q()
    q_object.add(Q(status=True), Q.OR)
    q_object.add(Q(start_date_disable__lte=date) & Q(end_date_disable__gte=date), Q.OR)

    DisableManager.objects.filter(q_object).update(status_current=True)
    part_disable = DisableManager.objects.filter(q_object)
    data = DisableManagerSerializer(part_disable, many=True).data
    f = open(settings.BASE_DIR + '/static/DisableManager.json', 'w')
    print(f)
    f.write(json.dumps(data))
    f.close()
    AppDisableList.load_app_list()


class ThreadMakeJson(threading.Thread):
    def __init__(self, interval):
        threading.Thread.__init__(self)
        self.interval = interval

    def run(self):
        while True:
            make_json_disable_manager()
            time.sleep(self.interval)
