from django.contrib import admin

from apps.common.admin import ProvinceFilter, CountyFilter
from apps.emtiaz.models import (
    Param,
    ActivityComment,
    HistoryScore,
    ParamActivityComment
)


class ActivityCommentAdmin(admin.ModelAdmin):
    list_display = ('activity', 'sender', 'status', 'create_at')


class ParamActivityCommentAdmin(admin.ModelAdmin):
    list_display = ('activity_comment', 'param', 'value')


class HistoryScoreAdmin(admin.ModelAdmin):
    search_fields = ('school__name',)
    list_filter = ('school__gender', 'created_at', ProvinceFilter, CountyFilter)
    list_display = ('school', 'g1', 'g2', 'g3', 'percent', 'g4', 'count_all_activity', 'count_best_activity', "created_at", 'final_point')
    fields = [
        ('school', 'final_point'),
        'count_all_activity',
        'count_best_activity',
        'g1',
        'g2',
        ('g3', 'percent'),
        'g4',
    ]
    readonly_fields = ('school',)


admin.site.register(Param)
admin.site.register(ParamActivityComment, ParamActivityCommentAdmin)
admin.site.register(ActivityComment, ActivityCommentAdmin)
admin.site.register(HistoryScore, HistoryScoreAdmin)
