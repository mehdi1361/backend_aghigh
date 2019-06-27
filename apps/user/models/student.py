from django.contrib.auth.hashers import make_password
from django.db import models
from django.utils.translation import ugettext as _
from django.utils.timezone import datetime

from apps.league.models import School
from apps.user.models.base import BaseUser


class Student(BaseUser):
    school = models.ForeignKey(to=School)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)

    class Meta:
        verbose_name = _("Student")
        verbose_name_plural = _("Student")

    def save(self, *args, **kwargs):
        if self.id is None:
            self.password = make_password(self.password)
        super(Student, self).save(*args, **kwargs)


class ActivationBySmsCode(models.Model):
    user = models.ForeignKey(to=BaseUser, null=True, blank=True, default=None)
    activation_code = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    send_at = models.DateTimeField(default=datetime.now)
    is_active = models.BooleanField(default=True)

    def created_sms_persian_date(self):
        from apps.common.utils import gregorian_to_persian_chart
        if self.created_at:
            return gregorian_to_persian_chart(self.created_at, str_type="%Y/%m/%d %H:%M:%S")
        else:
            return ""

    created_sms_persian_date.admin_order_field = 'created_at'
