from django.utils.translation import ugettext as _
from django.db import models


class Reports(models.Model):
    view_count = models.PositiveIntegerField(default=0)
    activity_count = models.PositiveIntegerField(default=0)
    school_count = models.PositiveIntegerField(default=0)
    # activity accept avg count
    accept_avg = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_("Created at"))

    # def __str__(self):
    #     return self.view_count

    # class Meta:
    #     ordering = ['title']
    #     verbose_name = _("Activity Category")
    #     verbose_name_plural = _("Activity Categories")
