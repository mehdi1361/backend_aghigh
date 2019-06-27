from django.contrib import admin
from django.core.cache import cache
from apps.announcements.models import (
    Announcement,
    AnnouncementFile,
    AnnouncementReceiver,
     AnnouncementSeenHistory)
from django.utils.translation import ugettext as _


class AnnouncementFileInline(admin.StackedInline):
    model = AnnouncementFile
    extra = 0


class AnnouncementReceiverInline(admin.StackedInline):
    model = AnnouncementReceiver
    # raw_id_fields = ('camp', )
    exclude = ('school', )
    extra = 0


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_user')
    search_fields = ('title', )
    exclude = ('creator',)

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            fields = [
                'title',
                'description',
                'view_count',
                'image',
                ('has_date', 'date'),
            ]
        else:
            fields = [
                'title',
                'description',
                'image',
                ('has_date', 'date'),
            ]
        return fields

    inlines = [AnnouncementReceiverInline, AnnouncementFileInline]

    def get_user(self, obj):
        return obj.creator.first_name + " " + obj.creator.last_name

    get_user.short_description = _("User")

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        obj.creator_id = request.user.id

        obj.save()
        cache.clear()


# class AnnouncementVisitAdmin(admin.ModelAdmin):
#     list_display = ('announcement', 'user')
#     search_fields = ('announcement__title', )


class AnnouncementSeenHistoryAdmin(admin.ModelAdmin):
    list_display = ('announcement', 'get_user')
    search_fields = ('announcement__title', 'user__first_name', 'user__last_name')

    def get_user(self, obj):
        return obj.user.first_name + " " + obj.user.last_name

    get_user.short_description = _("User")

admin.site.register(Announcement, AnnouncementAdmin)
# admin.site.register(AnnouncementVisit, AnnouncementVisitAdmin)
admin.site.register(AnnouncementSeenHistory, AnnouncementSeenHistoryAdmin)
