import datetime
from django.contrib import admin

from apps.common.models import File, Image, ApkRelease, ApkChangeRelease, DisableManager
from apps.league.models import Province, County, School
from apps.user.models import Student
from apps.activity.models import Activity
from apps.emtiaz.models import HistoryScore


# Province filter
class ProvinceFilter(admin.SimpleListFilter):
    title = 'province'
    parameter_name = 'province__exact'

    def lookups(self, request, model_admin):
        provinces = []
        provinces_obj = Province.objects.all().order_by('title')
        for item in provinces_obj:
            provinces.append((item.slug, item.title))

        return tuple(provinces)

    def queryset(self, request, queryset):
        if self.value():
            if queryset.model == HistoryScore:
                return queryset.filter(school__province__slug=self.value())

            if queryset.model == School:
                return queryset.filter(province__slug=self.value())

            if queryset.model == Student:
                return queryset.filter(school__province__slug=self.value())

            if queryset.model == Activity:
                return queryset.filter(school__province__slug=self.value())

        return queryset


# County filter
class CountyFilter(admin.SimpleListFilter):
    title = 'county'
    parameter_name = 'county__exact'

    def lookups(self, request, model_admin):
        if request.GET.get('province__exact'):
            counties = []
            counties_obj = County.objects.filter(province__slug=request.GET.get('province__exact')).order_by('title')
            for item in counties_obj:
                counties.append((item.slug, item.title))

            return tuple(counties)

    def queryset(self, request, queryset):
        if self.value():
            if queryset.model == HistoryScore:
                return queryset.filter(school__county__slug=self.value())

            if queryset.model == School:
                return queryset.filter(county__slug=self.value())

            if queryset.model == Student:
                return queryset.filter(school__county__slug=self.value())

            if queryset.model == Activity:
                return queryset.filter(school__county__slug=self.value())
        return queryset


class ApkChangeReleaseInline(admin.StackedInline):
    model = ApkChangeRelease
    extra = 0


class DisableManagerInline(admin.StackedInline):
    fields = ('id_part', 'parent_id', 'name_part', 'status', 'status_current', 'admin_access')
    model = DisableManager
    extra = 0


class FileAdmin(admin.ModelAdmin):
    pass


class ImageAdmin(admin.ModelAdmin):
    pass


class ApkReleaseAdmin(admin.ModelAdmin):
    inlines = [ApkChangeReleaseInline]
    list_display = ('version', 'type', 'created_at', 'force_update', 'allow_run_app')


class DisableManagerAdmin(admin.ModelAdmin):
    inlines = [DisableManagerInline]
    list_display = (
        'id_part',
        'name_part',
        'status',
        'status_current',
        'start_date_disable',
        'end_date_disable',
    )
    ordering = ('id_part',)
    readonly_fields = ('status_current',)

    fields = (
        'id_part',
        'parent_id',
        'name_part',
        'status',
        'status_current',
        'admin_access',
        'start_date_disable',
        'end_date_disable',
        'message_disable',
    )

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """

        if form.cleaned_data['status']:
            obj.status_current = form.cleaned_data['status']
        else:
            if form.cleaned_data['start_date_disable'] is not None and form.cleaned_data['end_date_disable'] is not None:
                date = datetime.datetime.now()
                if form.cleaned_data['start_date_disable'] <= date <= form.cleaned_data['end_date_disable']:
                    obj.status_current = True
                else:
                    obj.status_current = False
            else:
                obj.status_current = False
        obj.save()


admin.site.register(File, FileAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(ApkRelease, ApkReleaseAdmin)
admin.site.register(DisableManager, DisableManagerAdmin)
