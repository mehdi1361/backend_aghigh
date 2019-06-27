from django.contrib import admin
from apps.report.models import Reports


# class RuleAdmin(admin.ModelAdmin):
#     list_display = ('name',)
#     list_filter = ('frequency',)
#     search_fields = ('name', 'description')


admin.site.register(Reports)
