import json
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from apps.common.models import DisableManager, ApkRelease
from apps.common.view import make_json_disable_manager


# kahrizi
# سیگنالی که موقع حذف و ذخیره هر ایتم در جدول مدیریت غیرفعال بودن صدا زده می شود
# این تابع تابع سازنده جیسون را صدا می زند تا همیشه آخرین تغییرالت در فایل حیسون باشد
from apps.common.viewsets import set_cache_apk_release_student, set_cache_apk_release_teacher, set_cache_apk_release_hamraz


@receiver(post_delete, sender=DisableManager)
@receiver(post_save, sender=DisableManager)
def disable_manage_modified_handler(sender, **kwargs):
    make_json_disable_manager()


# kahrizi
# سیگنالی که موقع حذف و ذخیره هر ایتم در جدول برنامه موبایل صدا زده می شود
# این تابع تابع سازنده جیسون را صدا می زند تا همیشه آخرین تغییرالت در فایل حیسون باشد
@receiver(post_delete, sender=ApkRelease)
@receiver(post_save, sender=ApkRelease)
def apk_release_modified_handler(sender, instance, **kwargs):
    if instance.type == "student":
        set_cache_apk_release_student()
    elif instance.type == "teacher":
        set_cache_apk_release_teacher()
    elif instance.type == "hamraz":
        set_cache_apk_release_hamraz()
