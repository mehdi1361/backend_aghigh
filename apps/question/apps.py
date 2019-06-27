from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class QuestionConfig(AppConfig):
    name = 'apps.question'
    verbose_name = _("Question")
