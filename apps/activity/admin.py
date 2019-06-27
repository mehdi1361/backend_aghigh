import datetime

from django.contrib import admin
from django.utils.html import format_html
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from urllib.parse import unquote

from utils.converters import sizeof_fmt

from dashboard.logger import logger_v1
from apps.emtiaz.tasks import computing_point_activity
from apps.notification.tasks import send_notification_student_activity
from apps.activity.models import (
    AdditionalField,
    ActivityCategory,
    Activity,
    DropDownFormSomeAdditionalField,
    FileActivity,
    ImageActivity,
    Department,
    ActivityAdditionalFields,
    GroupAdditionalFields,
    RateActivity,
    CategoriesReport,
    ReportAbuse
)
from apps.common.admin import ProvinceFilter, CountyFilter


class DropDownFormSomeAdditionalFieldInline(admin.StackedInline):
    fields = ('value', 'group_select')
    model = DropDownFormSomeAdditionalField
    fk_name = "additional_field"
    extra = 0


class AdditionalFieldInline(admin.StackedInline):
    fields = (
        'label',
        'func_name',
        'func_total_type',
        'params',
        'field_type',
        'required',
        'group',
        'order',
    )
    model = AdditionalField
    extra = 0


class ActivityCategoryAdmin(admin.ModelAdmin):
    # inlines = [AdditionalFieldInline]
    list_display = ('title', 'department', 'status')
    search_fields = ('title',)
    actions = ['activate_status', 'deactivate_status']

    save_as = True

    @staticmethod
    def activate_status(modelAdmin, request, queryset):
        for cat in queryset:
            cat.status = True
            cat.save()

    @staticmethod
    def deactivate_status(modelAdmin, request, queryset):
        for cat in queryset:
            cat.status = False
            cat.save()


class RateActivityAdmin(admin.ModelAdmin):
    list_display = ('activity', 'student', 'rate', 'point_student', 'average_absolute')


class GroupAdditionalFieldsAdmin(admin.ModelAdmin):
    list_display = ('label', 'order')
    search_fields = ('label', )


def copy_additional_field(modeladmin, request, queryset):
    for additional_field in queryset:
        additional_field.pk = None
        additional_field.save()


copy_additional_field.short_description = 'کپی'


# group filter
class GroupFilter(admin.SimpleListFilter):
    title = 'group'
    parameter_name = 'group__exact'

    def lookups(self, request, model_admin):
        groups = []
        groups_obj = GroupAdditionalFields.objects.all().order_by('label')
        for item in groups_obj:
            groups.append((item.id, item.label))

        return tuple(groups)

    def queryset(self, request, queryset):
        if self.value():
                return queryset.filter(group_id=self.value())
        return queryset


class AdditionalFieldAdmin(admin.ModelAdmin):
    list_display = ('label', 'group', 'category')
    list_filter = ('field_type', GroupFilter)
    search_fields = ('label',)
    save_as = True
    actions = [copy_additional_field]

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, unquote(object_id))

        if obj.field_type == 'drop_down':
            self.inlines = [DropDownFormSomeAdditionalFieldInline]
        else:
            self.inlines = []

        return super(AdditionalFieldAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)


class ActivityAdditionalFieldAdmin(admin.ModelAdmin):
    list_display = ('activity', 'status')


class DepartmentAdmin(admin.ModelAdmin):
    pass


class FileActivityInline(admin.StackedInline):
    model = FileActivity
    extra = 0

    def get_queryset(self, request):
        qs = super(FileActivityInline, self).get_queryset(request)
        return qs.filter(archive=False)

    def get_readonly_fields(self, request, obj=None):
        return ['file_link']


class ImageActivityInline(admin.StackedInline):
    model = ImageActivity
    fields = ['title', 'image_med', 'status', 'comment']

    can_delete = False
    extra = 0

    def get_queryset(self, request):
        qs = super(ImageActivityInline, self).get_queryset(request)
        return qs.filter(archive=False)

    def get_readonly_fields(self, request, obj=None):
        return ['image_med']


class ActivityAdditionalFieldsInline(admin.StackedInline):
    model = ActivityAdditionalFields
    extra = 0
    readonly_fields = ('additional_field',)


def ban_activity(modeladmin, request, queryset):
    for activity in queryset:
        activity.state = "BAN"
        activity.save()


ban_activity.short_description = 'عدم رعایت ضوابط'


class ActivityAdmin(admin.ModelAdmin):
    inlines = [ActivityAdditionalFieldsInline, FileActivityInline, ImageActivityInline]
    # list_display = ('title', 'state', 'vip', 'point', 'get_school_name', 'get_student_name', 'get_coach', 'get_province_name', 'created_at', 'accepted_at', 'updated_at')
    list_display = ('title', 'state', 'vip', 'point', 'get_school_name', 'get_student_name', 'get_coach', 'get_province_name', 'created_persian_date', 'accepted_persian_date', 'updated_persian_date')
    search_fields = ('title', 'school__name', 'student__first_name', 'student__last_name', 'checker__first_name', 'checker__last_name')
    list_filter = ('category', 'gender', 'state', 'vip', 'created_at', ProvinceFilter, CountyFilter)
    fields = [
        'student',
        'checker',
        'vip',
        'gender',
        'reject_count',
        'state',
        ('category', 'category_comment', 'category_status'),
        ('title', 'title_comment', 'title_status'),
        ('location', 'location_comment', 'location_status'),
        ('start_date', 'start_date_comment', 'start_date_status'),
        ('end_date', 'end_date_comment', 'end_date_status'),
        ('description', 'description_comment', 'description_status'),
        'general_comment'
    ]
    readonly_fields = ('student', 'checker', 'reject_count')
    actions = [ban_activity, ]

    def save_formset(self, request, form, formset, change):
        """in function baraye in neveshte shod ke vaghti fildi taiid mishod baghie filed hash taghiir peyda mikard"""
        instances = formset.save(commit=False)
        # model = ""
        # if formset.model == ActivityAdditionalFields:
        #     model = ActivityAdditionalFields
        # elif formset.model == ImageActivity:
        #     model = ImageActivity
        # elif formset.model == FileActivity:
        #     model = FileActivity

        for instance in instances:
            # try:
            #     row = model.objects.filter(id=instance.id).get()
            # except model.DoesNotExist:
            #     row = None

            # if row and row.status:
            #     continue
            instance.save()
        formset.save_m2m()

    def save_related(self, request, form, formsets, change):
        form.save_m2m()
        for formset in formsets:
            self.save_formset(request, form, formset, change=change)

        # formset = formsets[0]
        # activity_id = formset.instance.id
        # activity = Activity.objects.filter(id=activity_id)
        # boo_general = self.get_status_activity(activity)
        # additional_field = ActivityAdditionalFields.objects.filter(activity_id=activity_id, status=False)
        # image = ImageActivity.objects.filter(activity_id=activity_id, status=False, archive=False)
        # file = FileActivity.objects.filter(activity_id=activity_id, status=False, archive=False)

        # if not image and not additional_field and not file and boo_general:
        #     activity.update(state="ACCEPT", accepted_at=datetime.datetime.now(), updated_at=datetime.datetime.now())
        #     try:
        #         computing_point_activity(activity_id)
        #     except Exception as e:
        #         logger_v1.error("Activity Admin condition_computer Error", extra={
        #             "detail": {
        #                 "error": e,
        #             }
        #         })
        # else:
        #     activity.update(state="SHE")
        #     send_notification_student_activity(activity.get())
        #     try:
        #         activity.update(checker=request.user.baseuser.teacher.id)
        #     except:
        #         pass

    @staticmethod
    def get_status_activity(activity):
        activity = activity.get()
        if activity.title_status and activity.location_status and activity.start_date_status and \
                activity.end_date_status and activity.category_status and activity.description_status:
            return True
        return False


class ImageActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'print_image_size', 'generate_thumbnails']

    actions = ['bulk_generate_thumbnails', ]

    @staticmethod
    def bulk_generate_thumbnails(modelAdmin, request, queryset):
        for image in queryset:
            image.image.generate_thumbnails()

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^(?P<image_id>.+)/generate/$',
                self.admin_site.admin_view(self.process_generate_thumbnails),
                name='image_process_generate_thumbnails',
            ),
        ]
        return custom_urls + urls

    def process_generate_thumbnails(self, request, image_id, *args, **kwargs):
        image = ImageActivity.objects.get(id=image_id)
        image.obj.generate_thumbnails()

        redirect_url = reverse(
            'admin:common_image_changelist',
            current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(redirect_url)

    def print_image_size(self, obj):
        return format_html('{}', sizeof_fmt(int(obj.size)))

    def generate_thumbnails(self, obj):
        return format_html(
            '<a class="button" href="{}">Generate Thumbnails</a>',
            reverse('admin:image_process_generate_thumbnails', args=[obj.pk]),
        )

    print_image_size.short_description = 'Image Size'
    generate_thumbnails.short_description = ''
    bulk_generate_thumbnails.short_description = 'Generate Thumbnails'
    generate_thumbnails.allow_tags = True


class DropDownFormSomeAdditionalFieldAdmin(admin.ModelAdmin):
    list_display = ['value', 'additional_field']
    search_fields = ['additional_field__label', 'value']
    list_filter = ['additional_field']
    filter_horizontal = ['group_select']


class ReportAbuseAdmin(admin.ModelAdmin):
    list_display = ['activity', 'sender', 'category', 'seen']
    search_fields = ('activity', )
    list_filter = ('category', )
    readonly_fields = ('activity', 'sender', 'category', 'content')

admin.site.register(ImageActivity, ImageActivityAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityCategory, ActivityCategoryAdmin)
admin.site.register(AdditionalField, AdditionalFieldAdmin)
admin.site.register(GroupAdditionalFields, GroupAdditionalFieldsAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(RateActivity, RateActivityAdmin)
admin.site.register(CategoriesReport)
admin.site.register(ReportAbuse, ReportAbuseAdmin)
admin.site.register(DropDownFormSomeAdditionalField, DropDownFormSomeAdditionalFieldAdmin)
admin.site.register(ActivityAdditionalFields)
