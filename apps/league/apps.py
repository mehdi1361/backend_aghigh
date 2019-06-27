from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LeagueConfig(AppConfig):
    name = 'apps.league'
    verbose_name = _("League")
