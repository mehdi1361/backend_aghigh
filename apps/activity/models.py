import datetime

from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext as _
from django.db import models
from django.utils.safestring import mark_safe
from apps.activity import static
from apps.user.models.teacher import Teacher
from apps.user.models.student import Student
from apps.user.models.base import BaseUser
from apps.common.helpers.media_filename_hash import MediaFileNameHash
from apps.league.models import Department, School
from apps.common.fields import ImageWithThumbsField
from apps.common.utils import gregorian_to_persian_chart


class ActivityCategory(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    slug = models.CharField(max_length=255, verbose_name=_("Slug"))
    department = models.ForeignKey(to=Department, verbose_name=_("Department"), default=1)
    status = models.BooleanField(default=True, verbose_name=_("Status"))
    max_count_activity = models.PositiveIntegerField(verbose_name=_("Max Count Activity"), default=0)
    # فیلد زیر برای مخفی کردن آیتم در لیست دسته فعالیت ها بخصوص موبایل است
    hide_in_list_web = models.BooleanField(default=False, verbose_name=_("Hide in List Web"))
    hide_in_list_app = models.BooleanField(default=False, verbose_name=_("Hide in List App"))

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name = _("Activity Category")
        verbose_name_plural = _("Activity Categories")


class GroupAdditionalFields(models.Model):
    label = models.CharField(
        max_length=45,
        null=True,
        blank=True,
        verbose_name=_("Label")
    )

    order = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Order"),
        choices=static.order_choice,
    )

    child_group = models.BooleanField(default=False, verbose_name=_("Child Group"))

    show_lable = models.BooleanField(default=True, verbose_name=_("Show Lable"))

    def __str__(self):
        return self.label


class AdditionalField(models.Model):
    label = models.CharField(max_length=45, verbose_name=_("Label"))

    order = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("order"),
        choices=static.order_choice,
    )

    func_name = models.CharField(
        max_length=45,
        null=True,
        blank=True,
        choices=static.function_additional_fields_choice,
        verbose_name=_("Function name")
    )
    func_total_type = models.CharField(
        max_length=45,
        null=True,
        blank=True,
        choices=static.function_additional_fields_total_number_type,
        verbose_name=_("Function total type")
    )
    params = models.TextField(verbose_name=_("Params"), default=0)

    field_type = models.CharField(max_length=12, choices=static.field_type_choice, verbose_name=_("Field type"))
    category = models.ForeignKey(to=ActivityCategory, verbose_name=_("Category"))

    group = models.ForeignKey(to=GroupAdditionalFields, verbose_name=_("Group"), null=True)

    required = models.BooleanField(default=False)

    validate_data = JSONField(default={}, null=True, blank=True)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = _("Additional Field")
        verbose_name_plural = _("Additional Fields")

    def get_drop_down(self):
        # values = DropDownFormSomeAdditionalField.objects.filter(additional_field_id=self.id).values('id', 'value', 'sub_form_id')
        drop_down_form = DropDownFormSomeAdditionalField.objects.filter(additional_field_id=self.id).prefetch_related("group_select")
        # کد زیر برای این اضافه شد که اگر مقدار دراپ باکس مقداری نداشت نان برنگرداند بلکه -۱ برگرداند
        values = []
        for item in drop_down_form:
            option_dict = {"id": item.id, "value": item.value, "group_select_id": -1}
            if list(item.group_select.all()):
                option_dict['group_select_id'] = item.id
            values.append(option_dict)

        return values


class DropDownFormSomeAdditionalField(models.Model):
    value = models.CharField(max_length=255, verbose_name=_("value"))
    additional_field = models.ForeignKey(to=AdditionalField, related_name='additional_field')

    #  این فیلد برای کمبوباکس هایی اضافه شده که به ازای انتخاب  آیتم های آن باید کدام گروه را  نشان داده شود
    group_select = models.ManyToManyField(GroupAdditionalFields, verbose_name=_("Group Select"), blank=True)

    # group_selected_id = models.IntegerField(default=None, blank=True, null=True)

    #  این فیلد برای کمبوباکس هایی اضافه شده که به ازای انتخاب  آیتم های آن باید یک زیر فرم نشان داده شود
    # sub_form_selected = models.ForeignKey(to=AdditionalField, default=None, blank=True, null=True, related_name='sub_form_selected')
    # فیلد زیر آی دی ساب فورم فوق را نگه می دارد
    # sub_form_id = models.IntegerField(default=None, blank=True, null=True)

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    #     self.sub_form_id = self.sub_form_selected.id;
    #     return super(DropDownFormSomeAdditionalField, self).save()

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    #     self.group_selected_id = self.group_select.id
    #     return super(DropDownFormSomeAdditionalField, self).save()

    # def get_group_select_id(self):
    #     if self.group_select:
    #         return self.group_select.id
    #     else:
    #         return -1

    def __str__(self):
        return self.value

    class Meta:
        verbose_name = _("Drop Down Form Some Additional Field")


class Activity(models.Model):
    school = models.ForeignKey(
        to=School,
        verbose_name=_("School"),
        default=14151
    )

    student = models.ForeignKey(
        to=Student,
        related_name="activity_student",
        verbose_name=_("Student"),
    )

    checker = models.ForeignKey(
        to=Teacher,
        related_name="activity_checker",
        verbose_name=_("Checker"),
        null=True,
        blank=True
    )

    category = models.ForeignKey(to=ActivityCategory, verbose_name=_("Category"))
    category_status = models.BooleanField(default=False, verbose_name=_("Category Status"))
    category_comment = models.CharField(max_length=255, verbose_name=_("Comment"), null=True, blank=True)

    title = models.CharField(max_length=255, verbose_name=_("Title"))
    title_comment = models.CharField(max_length=255, verbose_name=_("Comment"), null=True, blank=True)
    title_status = models.BooleanField(default=False, verbose_name=_("Title status"))

    location = models.CharField(max_length=255, verbose_name=_("Location"))
    location_comment = models.CharField(max_length=255, verbose_name=_("Comment"), null=True, blank=True)
    location_status = models.BooleanField(default=False, verbose_name=_("Location status"))

    start_date = models.DateTimeField(verbose_name=_("Start time date"))
    start_date_comment = models.CharField(max_length=255, verbose_name=_("Comment"), null=True, blank=True)
    start_date_status = models.BooleanField(default=False, verbose_name=_("Start date status"))

    end_date = models.DateTimeField(verbose_name=_("End time date"))
    end_date_comment = models.CharField(max_length=255, verbose_name=_("Comment"), null=True, blank=True)
    end_date_status = models.BooleanField(default=False, verbose_name=_("End date status"))

    description = models.TextField(verbose_name=_("Description"))
    description_comment = models.CharField(max_length=255, verbose_name=_("Comment"), null=True, blank=True)
    description_status = models.BooleanField(default=False, verbose_name=_("Description status"))

    general_comment = models.TextField(verbose_name=_("General comment"), null=True, blank=True)

    state = models.CharField(max_length=10, choices=static.activity_state_choice, verbose_name=_("Activity State"),
                             default='NEW')

    comments_count = models.PositiveSmallIntegerField(default=0, verbose_name=_("Comments Count"))

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Updated at"))
    accepted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Accepted at"))

    vip = models.BooleanField(default=False, verbose_name=mark_safe(_("Vip") + "</br> "))
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)

    point_emtiaz = models.FloatField(default=0)  # Avg('rate') from rate table
    point_emtiaz_sum = models.PositiveIntegerField(default=0)  # Sum('average_absolute') from rate table

    point = models.PositiveIntegerField(default=0, verbose_name=_("Point System"))  # system point
    rate_count = models.PositiveIntegerField(default=0)
    reject_count = models.PositiveIntegerField(default=0, verbose_name=_("Reject count"))

    gender = models.CharField(
        max_length=10,
        choices=static.gender_choice,
        null=True, blank=True,
        verbose_name=_("Gender")
    )

    use_in_league = models.BooleanField(default=False, verbose_name=_("use_in_league"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")

    def _get_item_height(self):
        return self.created_at - self.end_date

    different_date = property(_get_item_height)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.id is None:
            self.state = 'NEW'
            self.gender = self.student.gender
            self.school = self.student.school

        super(Activity, self).save()

    def get_images(self):
        values = ImageActivity.objects.using(self._state.db).filter(activity_id=self.id, archive=False)
        return values

    def get_files(self):
        values = FileActivity.objects.using(self._state.db).filter(activity_id=self.id, archive=False)
        return values

    def get_additional_field(self):
        values = ActivityAdditionalFields.objects.using(self._state.db).filter(activity_id=self.id)
        return values

    def get_student(self):
        values = Student.objects.using(self._state.db).filter(student_id=self.student_id)
        return values

    def get_coach(self):
        # values = "-"
        # roles_all = self.school.teacher.coach_levels.all()
        # for role in roles_all:
        #     if role.level_code == "coach":
        #         values = role.title
        values = self.school.teacher.first_name + " " + self.school.teacher.last_name
        return values

    def get_school_name(self):
        return self.school.name

    def get_student_name(self):
        return self.student.first_name + " " + self.student.last_name

    get_coach.short_description = _('get_coach')
    get_student_name.short_description = _('get_student_name')

    get_school_name.short_description = _('get_school_name')
    get_school_name.admin_order_field = 'school'

    def get_province_name(self):
        return self.school.province.title

    get_province_name.short_description = _('get_province_name')
    get_province_name.admin_order_field = 'school__province'

    def get_county_name(self):
        return self.school.county.title

    get_province_name.short_description = _('get_province_name')
    get_province_name.admin_order_field = 'school__province'

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

    def accepted_persian_date(self):
        if self.accepted_at:
            return gregorian_to_persian_chart(self.accepted_at, str_type="%Y/%m/%d %H:%M:%S")
        else:
            return ""

    accepted_persian_date.admin_order_field = 'accepted_at'


def validate_file_extension(value):
    # ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.mp3', '.doc', '.docx', '.xlsx', '.xls', '.mp4', '.zip']
    # if not ext.lower() in valid_extensions:
    #     raise ValidationError(_('Unsupported file extension.'))


class ActivityState(models.Model):
    activity = models.ForeignKey(to=Activity)
    viewer = models.ForeignKey(to=BaseUser)
    viewer_ip = models.CharField(max_length=40, null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))

    class Meta:
        verbose_name = _("Activity State")
        verbose_name_plural = _("Activity State")
        unique_together = ('activity', 'viewer')

    def get_activity_view_count(self, activity):
        activities = self.objects.filter(activity=activity)
        return activities.count()


class ActivityLike(models.Model):
    activity = models.ForeignKey(to=Activity)
    liker = models.ForeignKey(to=BaseUser, null=True, blank=True, default=None)
    liker_ip = models.CharField(max_length=40, null=True, blank=True, default=None)
    liker_mime = models.CharField(max_length=40, null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_("Created at"))


class FileActivity(models.Model):
    file = models.FileField(
        upload_to=MediaFileNameHash("files"),
        verbose_name=_("Address")
    )
    activity = models.ForeignKey(to=Activity, verbose_name=_("Activity"))
    status = models.BooleanField(default=False, verbose_name=_("Accept"))
    size = models.CharField(max_length=150, default="", blank=True, null=True)
    title = models.CharField(max_length=150, default="", blank=True, null=True)
    comment = models.TextField(null=True, blank=True, verbose_name=_("Comment"))
    archive = models.BooleanField(default=False, verbose_name=_("Archive"))

    def file_link(self):
        return "<a href='/{0}' style='margin-right: 2%'>{1}</a>".format(self.file.url, _("Download"))

    file_link.allow_tags = True

    class Meta:
        verbose_name = _("FileActivity")
        verbose_name_plural = _("FileActivity")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.id is None:
            try:
                self.title = self.file.name.split("@")[0]
            except:
                pass
            self.size = self.file.size

        super(FileActivity, self).save()


class ImageActivity(models.Model):
    image = ImageWithThumbsField(
        upload_to=MediaFileNameHash("images"),
        default=None,
        sizes=((320, 180), (145, 145), (711, 400),),
        preserve_ratio=True,
        verbose_name=_("Address")
    )
    size = models.CharField(max_length=150, default="", blank=True, null=True)
    title = models.CharField(max_length=150, default="", blank=True, null=True)
    activity = models.ForeignKey(to=Activity, verbose_name=_("Activity"))
    status = models.BooleanField(default=False, verbose_name=_("Accept"))
    archive = models.BooleanField(default=False, verbose_name=_("Archive"))
    comment = models.TextField(null=True, blank=True, verbose_name=_("Comment"))

    def image_med(self):
        """تابع نمایش عکس کوچک در صفحه ادمین جنگو"""
        if "jpg" in self.image.url:
            img = self.image.url.replace(".jpg", ".711x400.jpg")
        else:
            img = self.image.url.replace(".jpeg", ".711x400.jpeg")
        return u'<img src="/{0}" style="{1}" {2}/>'.format(img, "width: 100%", 'height=150')
        # return u'<a href="'+self.image.url+'"><img src="/{0}" style="{1}" {2}/>'.format(img, "width: 100%", 'height=150')+"</a>"

    image_med.allow_tags = True

    def image_tag(self):
        return u'<img src="/{0}" style="{1}" {2}/>'.format(self.image.url, "width: 100%", 'height=150')

    image_tag.allow_tags = True

    class Meta:
        verbose_name = _("ImageActivity")
        verbose_name_plural = _("ImageActivity")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.id is None:
            try:
                self.title = self.image.name.split("@")[0]
            except:
                pass
            self.size = self.image.size

        super(ImageActivity, self).save()


class ActivityAdditionalFields(models.Model):
    activity = models.ForeignKey(to=Activity, verbose_name=_("Activity"))
    additional_field = models.ForeignKey(to=AdditionalField, verbose_name=_("Field Name"))
    value = models.TextField(
        verbose_name=_("Value"),
        null=True,
        blank=True,
    )
    status = models.BooleanField(default=False, verbose_name=_("Accept"))
    comment = models.TextField(null=True, blank=True, verbose_name=_("Comment"))

    class Meta:
        verbose_name = _("Field Status")
        verbose_name_plural = _("Field Statuses")

    def __str__(self):
        return self.activity.title + "-" + self.additional_field.label


class RateActivity(models.Model):
    activity = models.ForeignKey(to=Activity, related_name='Activity')
    student = models.ForeignKey(to=Student, related_name='Student')
    rate = models.PositiveIntegerField(default=1, choices=static.rate_choice)
    first_like = models.BooleanField(default=False, verbose_name=_("First Like"))

    point_student = models.PositiveIntegerField(default=0)
    average_absolute = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = _("Rate")
        verbose_name_plural = _("Rates")
        unique_together = ('activity', 'student')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.id is not None:
            self.updated_at = datetime.datetime.now()

        super(RateActivity, self).save()


class ActivityDailyReport(models.Model):
    activity = models.ForeignKey(to=Activity)

    view_count = models.PositiveIntegerField(default=0)
    point = models.PositiveIntegerField(default=0)
    date = models.DateField()

    class Meta:
        verbose_name = _("Activity daily report")
        verbose_name_plural = _("Activity daily report")


class StudentDailyReport(models.Model):
    student = models.ForeignKey(to=Student)

    point = models.PositiveIntegerField(default=0)
    date = models.DateField()

    class Meta:
        verbose_name = _("Student daily report")
        verbose_name_plural = _("Student daily report")


class CategoriesReport(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("title"))

    class Meta:
        verbose_name = _("Categories report")
        verbose_name_plural = _("Categories reports")

    def __str__(self):
        return self.title


class ReportAbuse(models.Model):
    activity = models.ForeignKey(to=Activity)
    sender = models.ForeignKey(to=Student)
    category = models.ForeignKey(to=CategoriesReport, verbose_name=_('category'))
    content = models.CharField(max_length=255, verbose_name=_('content'), null=True, blank=True)
    seen = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        verbose_name = _("Report Abuse")
        verbose_name_plural = _("Report Abuses")
        unique_together = ('activity', 'sender')

    def __str__(self):
        return self.activity.title
