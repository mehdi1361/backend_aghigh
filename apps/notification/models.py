from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.postgres.fields import JSONField


class FcmTokenUser(models.Model):
    user = models.ForeignKey(to=User, related_name="User")
    web_token = models.CharField(max_length=255, null=True, blank=True)
    mobile_token = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = _("FcmToken User")
        verbose_name_plural = _("FcmToken User")


class Notification(models.Model):
    send_to = models.ForeignKey(User, related_name="notification_receiver", verbose_name=_("Receiver"))
    seen = models.BooleanField(default=False, verbose_name=_("Seen"))
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    body = models.TextField(verbose_name=_("body"))
    created_date = models.DateTimeField(auto_now=True, verbose_name=_("Date Time"))

    body_action = JSONField(
        verbose_name=_("body_action"),
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
