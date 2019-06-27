from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CalenderConfig(AppConfig):
    name = 'apps.schedule'
    verbose_name = _("schedule")
