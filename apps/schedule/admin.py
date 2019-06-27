from django.contrib import admin

from apps.schedule.models import Event, Occurrence, Rule
from apps.schedule.models.annual import AnnualEvents
from apps.schedule.utils import get_admin_model_fields


class AnnualEventsAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'date_type',
        'day',
        'month',
    )


class CalendarAdminOptions(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    fieldsets = (
        (None, {
            'fields': [
                          ('name', 'slug'),
                      ] + get_admin_model_fields('Calendar')
        }),
    )


class CalendarRelationAdmin(admin.ModelAdmin):
    list_display = ('calendar', 'content_object')
    list_filter = ('inheritable',)
    fieldsets = (
        (None, {
            'fields': [
                'calendar',
                ('content_type', 'object_id', 'distinction',),
                'inheritable',
            ]
        }),
    )


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start', 'end')
    list_filter = ('start',)
    ordering = ('-start',)
    date_hierarchy = 'start'
    search_fields = ('title', 'description')
    fieldsets = (
        (None, {
            'fields': [
                          ('title', 'color_event'),
                          ('description',),
                          ('start', 'end'),
                          ('creator', 'calendar'),
                          ('rule', 'end_recurring_period'),
                      ] + get_admin_model_fields('Event')
        }),
    )


class RuleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('frequency',)
    search_fields = ('name', 'description')


admin.site.register(AnnualEvents, AnnualEventsAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(Occurrence, admin.ModelAdmin)
