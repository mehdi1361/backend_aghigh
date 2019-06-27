from django import forms
from django.contrib import admin

from apps.league.models import Province, County, School
from apps.user.export_csv import export_xls_teacher
from apps.user.forms import StudentForm, TeacherForm, AdvisorForm
from apps.user.models import Advisor
from apps.user.models.advisor import AdvisorLevel
from apps.user.models.base import BaseUser
from apps.user.models.student import Student, ActivationBySmsCode
from apps.user.models.teacher import Teacher, CoachLevel
from apps.common.admin import ProvinceFilter, CountyFilter
from utils.user_type import get_user_type, get_user_location_name


class StudentAdmin(admin.ModelAdmin):
    list_filter = (
        ProvinceFilter,
        CountyFilter,
        'gender',
        'last_visit',
        'is_active',
    )
    search_fields = ('first_name', 'last_name', 'username', 'phone_number')
    list_display = ('__str__', 'school', 'get_province_county_camp_name', 'is_active')
    raw_id_fields = ('school',)

    def get_exclude(self, request, obj=None):

        """
            this function override'ed to add Student form
            to modify password field
        """

        if obj:
            self.form = StudentForm
        else:
            self.form = forms.ModelForm
        return self.exclude

    @staticmethod
    def get_province_county_camp_name(obj):

        return obj.school.province.title + " > " + obj.school.county.title


class TeacherAdmin(admin.ModelAdmin):
    list_filter = (
        'gender',
        'coach_levels',
        'last_visit',
        'is_active'
    )
    search_fields = ('first_name', 'last_name', 'username', 'phone_number')
    # list_display = ('__str__', 'get_coach_levels')
    actions = [export_xls_teacher]

    list_display = ('__str__', 'get_coach_levels', 'get_province_county_name', 'is_active')

    @staticmethod
    def get_coach_levels(obj):
        return "\n ,".join([p.title for p in obj.coach_levels.all()])

    def get_exclude(self, request, obj=None):
        if obj:
            self.form = TeacherForm
        else:
            self.form = forms.ModelForm

        return self.exclude

    @staticmethod
    def get_province_county_name(obj):
        levels = [p.level_code for p in obj.coach_levels.all()]
        full_name = "مکان نامشخص"
        if 'coach' in levels:
            try:
                school = obj.school_set.all()[0]
                full_name = school.province.title + " > " + school.county.title
            except:
                full_name = "بدون مدرسه"

        elif 'camp' in levels:
            try:
                camp = obj.camp_set.all()[0]
                full_name = camp.province.title + " > " + camp.county.title
            except:
                full_name = "بدون قرارگاه"

        elif 'county' in levels:
            try:
                county = obj.county_set.all()[0]
                full_name = county.province.title
            except:
                full_name = "بدون شهرستان"

        elif 'province' in levels:
            try:
                province = obj.province_set.all()[0]
                full_name = province.title
            except:
                full_name = "بدون استان"

        elif 'country' in levels:

            full_name = "مسول کل"

        return full_name


class AdvisorAdmin(admin.ModelAdmin):
    list_filter = ('gender',)
    search_fields = ('first_name', 'last_name')
    list_display = ('__str__', 'get_coach_levels')

    @staticmethod
    def get_coach_levels(obj):
        return "\n ,".join([p.title for p in obj.levels.all()])

    def get_exclude(self, request, obj=None):
        if obj:
            self.form = AdvisorForm
        else:
            self.form = forms.ModelForm

        return self.exclude


class CoachLevelAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


class ProvinceInline(admin.StackedInline):
    model = Province
    extra = 0


class ProvinceAdmin(admin.ModelAdmin):
    inlines = [ProvinceInline]


class CountyInline(admin.StackedInline):
    model = County
    extra = 0


class SchoolCountyAdmin(admin.ModelAdmin):
    inlines = [CountyInline]


class ActivationBySmsCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'activation_code', 'user_phone_number', 'created_sms_persian_date', 'is_active')
    readonly_fields = ('created_at_field',)
    search_fields = ['user__first_name', 'user__last_name', 'user__id']

    list_filter = (
        # ProvinceFilter ,
        # CountyFilter ,
        'is_active',
    )

    @staticmethod
    def created_at_field(obj):
        return obj.created_at.strftime('%d %b %Y %H:%M:%S')

    # @staticmethod
    # def created_shamsi(obj):
    #     from apps.common.utils import gregorian_to_persian_chart
    #     return gregorian_to_persian_chart(obj.created_at) #.strftime('%d %b %Y %H:%M:%S')

    # created_shamsi.admin_order_field = 'created_at'

    @staticmethod
    def user_phone_number(obj):
        return obj.user.phone_number


# class MonitoringUserAdmin(admin.ModelAdmin):
#     list_display = ('user_full_name', 'user_type', 'phone_number', 'school', 'province', 'county', 'created_persian_date', 'updated_persian_date', 'last_login_persian_date', 'is_active', 'last_activation_code', 'last_activation_date')
#
#     camp_value = ""
#     county_value = ""
#     # province = ""
#
#     last_activation_date_value = ""
#
#     # list_display = ('user_full_name', 'user_type', 'user_phone_number', 'school', 'province', 'county', 'created_persian_date', 'baghery_sync_date', 'is_active', 'last_login', 'last_activation_code', 'last_activation_date')
#     # readonly_fields = ('created_at_field',)
#     # search_fields = ['user__first_name', 'user__last_name', 'user__id']
#
#     # list_filter = (
#     #     'user_type',
#     #     # province ,
#     #     # county ,
#     #     'is_active',
#     # )
#
#     @staticmethod
#     def user_full_name(obj):
#         return obj.get_full_name()
#
#     @staticmethod
#     def user_type(obj):
#         user_type = get_user_type(obj)
#         if user_type == "student":
#             return "دانش اموز"
#         elif user_type == "teacher":
#             return "مربی"
#         elif user_type == "advisor":
#             return "مشاور"
#         elif user_type == "admin":
#             return "مدیر"
#         else:
#             return ""
#
#     @staticmethod
#     def school(obj):
#         user_type = get_user_type(obj)
#         # school_name = ""
#
#         if user_type == "student":
#             school = Student.objects.get(pk=obj.pk).school
#             school_name = school.name
#             return school_name
#
#         elif user_type == "teacher":
#             # try:
#             #     # school = School.objects.get(teacher__pk=obj.pk)
#             # except:
#             #     return "بدون مدرسه"
#             # school_name = school.name
#             # return school_name
#             try:
#                 school = obj.teacher.school_set.all()[0]
#                 # full_name = school.province.title + " > " + school.county.title
#                 return school.name
#             except:
#                 return "بدون مدرسه"
#
#         elif user_type == "advisor":
#             return ""
#         elif user_type == "admin":
#             return ""
#         else:
#             return ""
#
#     @staticmethod
#     def province(obj):
#         camp, county, province = get_user_location_name(obj)
#
#         MonitoringUserAdmin.county_value = county
#         MonitoringUserAdmin.camp_value = camp
#
#         return province
#
#     @staticmethod
#     def county(obj):
#         # camp, county, province = get_user_location_name(obj)
#         return MonitoringUserAdmin.county_value
#
#     @staticmethod
#     def camp(obj):
#         # camp, county, province = get_user_location_name(obj)
#         return MonitoringUserAdmin.camp_value
#
#     @staticmethod
#     def last_activation_code(obj):
#         try:
#             sms = ActivationBySmsCode.objects.filter(user__pk=obj.pk).last()
#             if sms:
#                 MonitoringUserAdmin.last_activation_date_value = sms.created_sms_persian_date()
#                 return sms.activation_code
#             else:
#                 return ""
#
#         except ActivationBySmsCode.DoesNotExist:
#             return ""
#
#     @staticmethod
#     def last_activation_date(obj):
#         return MonitoringUserAdmin.last_activation_date_value
#         # try:
#         #     sms = ActivationBySmsCode.objects.filter(user__pk=obj.pk).last()
#         #     if sms:
#         #         MonitoringUserAdmin.last_activation_date1 = sms.created_persian_date()
#         #         return sms.created_sms_persian_date()
#         #     else:
#         #         return ""
#         #
#         # except ActivationBySmsCode.DoesNotExist:
#         #     return ""


admin.site.register(Advisor, AdvisorAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(CoachLevel, CoachLevelAdmin)
admin.site.register(AdvisorLevel)
admin.site.register(ActivationBySmsCode, ActivationBySmsCodeAdmin)
# admin.site.register(BaseUser, MonitoringUserAdmin)
