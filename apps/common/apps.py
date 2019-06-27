from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class CommonConfig(AppConfig):
    name = 'apps.common'
    verbose_name = _("Common")

    def ready(self):
        from apps.common import signal
        from pathlib import Path
        from apps.common.view import make_json_disable_manager, ThreadMakeJson
        json_file_disable_manager = Path(settings.BASE_DIR + '/static/DisableManager.json')
        if not json_file_disable_manager.is_file():
            make_json_disable_manager()

        # thread_generate_json = ThreadMakeJson(24 * 60 * 60)
        # thread_generate_json.start()
