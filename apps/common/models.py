import os
from django.utils.translation import ugettext as _
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.core.exceptions import ValidationError
from apps.common.helpers.media_filename_hash import MediaFileNameHash
from apps.common.utils import sizeof_fmt, remove_file
from apps.common.utils import gregorian_to_persian_chart


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.apk']
    if not ext.lower() in valid_extensions:
        raise ValidationError(_('Unsupported file extension.'))


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.

    """
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Updated at"))

    class Meta:
        abstract = True

    def created_persian_date(self):
        if self.created_at:
            return gregorian_to_persian_chart(self.created_at, str_type="%Y/%m/%d %H:%M:%S")
        else:
            return ""

    created_persian_date.admin_order_field = 'created_at'

    def updated_persian_date(self):
        if self.updated_at:
            return gregorian_to_persian_chart(self.updated_at, str_type="%Y/%m/%d %H:%M:%S")
        else:
            return ""

    updated_persian_date.admin_order_field = 'updated_at'


class ApkRelease(models.Model):
    type_choice = (
        ('student', 'student'),
        ('teacher', 'teacher'),
        ('hamraz', 'hamraz'),
    )
    version = models.FloatField(verbose_name=_("Version"))
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    message = models.TextField(verbose_name=_("Message"))
    type = models.CharField(max_length=10, choices=type_choice, verbose_name=_("Type App"))
    file = models.FileField(
        upload_to=MediaFileNameHash("files"),
        validators=[validate_file_extension],
        verbose_name=_("Address")
    )
    allow_run_app = models.BooleanField(default=False)
    force_update = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_("Created at"))

    def __str__(self):
        return str(self.version)

    class Meta:
        verbose_name = _("Apk Release")
        verbose_name_plural = _("Apk Release")


class ApkChangeRelease(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    app_release = models.ForeignKey(to=ApkRelease, verbose_name=_("ApkRelease"))

    class Meta:
        verbose_name = _("Apk Change Release")
        verbose_name_plural = _("Apk Change Release")


class Image(models.Model):
    state_choice = (
        ('act', 'activity'),
        ('sho', 'shop'),
        ('non', 'none'),
        ('adv', 'adv')
    )

    upload_folder = 'images'

    title = models.CharField(max_length=255, verbose_name=_("Title"))
    obj = models.ImageField(upload_to=MediaFileNameHash(upload_folder), default=None, verbose_name=_("Obj"))
    image_size = models.PositiveIntegerField(default=0, verbose_name=_("Image size"))
    gender = models.CharField(max_length=1, default=None, verbose_name=_("Gender"))
    state = models.CharField(max_length=3, choices=state_choice, default=None, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.image_size = self.obj.size
        super(Image, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        remove_file(self.obj.path)
        super(Image, self).delete(using=using, keep_parents=keep_parents)

    @property
    def image_size_readable(self):
        return sizeof_fmt(self.image_size)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")


class File(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    obj = models.FileField(upload_to=MediaFileNameHash('files'), default=None, verbose_name=_("Obj"))
    file_size = models.PositiveIntegerField(default=0, verbose_name=_("File size"))
    gender = models.CharField(max_length=1, default=None, verbose_name=_("Gender"))

    def save(self, *args, **kwargs):
        self.image_size = self.obj.size
        super(File, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        remove_file(self.obj.path)
        super(File, self).delete(using=using, keep_parents=keep_parents)

    @property
    def image_size_readable(self):
        return sizeof_fmt(self.image_size)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("File")
        verbose_name_plural = _("Files")


class DisableManager(models.Model):
    """
    مدل مربوط به اینکه بخش های مختلف برنامه غیرفعال است یا نه
    یا اینکه در چه تاریخی غیرفعال است

    """
    id_part = models.IntegerField(verbose_name=_('IdPart'), primary_key=True)
    parent_id = models.ForeignKey('self', null=True, blank=True)  # فیلد زیربرای اینکه مشخص شود پدر این بخش کدام است
    name_part = models.TextField(verbose_name=_('NamePart'))
    status = models.BooleanField(verbose_name=_('Status Disable'))
    status_current = models.NullBooleanField(verbose_name=_('Status Current'))  # وضعیت بعد از اعمال تاریخ این محاسبه می شود و از کاربر گرفته نمی شود
    admin_access = models.NullBooleanField(verbose_name=_('AdminAccess'))  # فیلد زیر برای این است که آیا در حالت غیرفعال ادمین امکان استفاده داشته باشد یا نه
    message_disable = models.TextField(verbose_name=_("MessageDisable"), null=True, blank=True)  # پیامی که در حالت غیر فعال بودن نشان می دهد
    start_date_disable = models.DateTimeField(null=True, blank=True, verbose_name=_("Start Date Disable"))  # تار یخ شروع غیر فعال کردن  خودکار این بخش
    end_date_disable = models.DateTimeField(null=True, blank=True, verbose_name=_("End Date Disable"))  # تاریخ پایان غیرفعال کردن خودکار این بخش
    hidden = models.NullBooleanField(null=True, blank=True, verbose_name=_('Hidden'))  # فیلد زیر برای این است که اگر بخش غیر فعال باشد مخفی بشود یا نه
    color = models.CharField(null=True, blank=True, verbose_name=_('Color'), max_length=6)  # فیلد زیر رنگی است در صورت غیرفعال بودن بخش کلید مربوطه را با چه رنگی نشان دهد
    alpha = models.FloatField(null=True, blank=True)  # فیلد زیر برای میزان شفافیت کلید غیرفعال شده است

    def __str__(self):
        return self.name_part + " Disable status : " + str(self.status)

    def __int__(self, id_part, name_part, parent_id, status_current, status, admin_access, message_disable, start_date, end_date, hidden, color, alpha):
        self.id_part = id_part
        self.name_part = name_part
        self.parent_id = parent_id
        self.status = status
        self.status_current = status_current
        self.admin_access = admin_access
        self.message_disable = message_disable
        self.start_date_disable = start_date
        self.end_date_disable = end_date
        self.hidden = hidden
        self.color = color
        self.alpha = alpha
        # super(DisableManager, self).__int__()

    class Meta:
        verbose_name = _("DisableManager")
        verbose_name_plural = _("مدیریت بخش های غیرفعال")
