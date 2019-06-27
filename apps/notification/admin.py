from django.contrib import admin
from apps.notification.models import Notification, FcmTokenUser


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'seen', 'created_date')
    list_filter = ('seen', 'created_date')

    def get_queryset(self, request):
        qs = super(NotificationAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(send_to=request.user.id)

    def get_object(self, request, object_id, from_field=None):
        Notification.objects.filter(id=object_id, send_to=request.user.id).update(seen=True)
        return super(NotificationAdmin, self).get_object(request, object_id, from_field=None)

    @staticmethod
    def user_full_name(obj):
        return obj.send_to.first_name + " " + obj.send_to.last_name


class FcmTokenUserAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', )

    @staticmethod
    def user_full_name(obj):
        return obj.user.first_name + " " + obj.user.last_name


admin.site.register(Notification, NotificationAdmin)
admin.site.register(FcmTokenUser, FcmTokenUserAdmin)
