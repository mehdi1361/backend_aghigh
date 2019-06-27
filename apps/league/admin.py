from django.contrib import admin

from apps.league.export_csv import export_xls_camp
from apps.league.models import Camp, School, Province, County
from apps.common.admin import ProvinceFilter, CountyFilter


class SchoolAdmin(admin.ModelAdmin):
    list_filter = (
        ProvinceFilter,
        CountyFilter,
        'gender',
    )
    list_display = ('name', 'gender', 'teacher', 'student_name', 'active')
    search_fields = ('name', 'code_bagheri','teacher__first_name','teacher__last_name','student__first_name','student__last_name')

    @staticmethod
    def student_name(obj):
        full_name = "بدون دانش آموز"
        try:
            stu = obj.student_set.all()[0]
            full_name = stu.first_name + " " + stu.last_name
        except:
            pass

        return full_name

    def lookup_allowed(self, lookup, value):
        return True


class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('title', 'code')


class CampAdmin(admin.ModelAdmin):
    actions = [export_xls_camp]
    list_display = ('title', 'county_title', 'county_province_title')

    @staticmethod
    def county_title(obj):
        return obj.county.title

    @staticmethod
    def county_province_title(obj):
        return obj.county.province.title


admin.site.register(School, SchoolAdmin)
admin.site.register(Camp, CampAdmin)
admin.site.register(County)
admin.site.register(Province, ProvinceAdmin)
