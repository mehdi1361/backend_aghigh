from django.utils.translation import ugettext as _
from django.contrib.auth.hashers import make_password
from django.db import models

from apps.user.models.base import BaseUser


class CoachLevel(models.Model):
    level_choices = (
        ('coach', 'Coach'),
        ('camp', 'Camp'),
        ('county', 'County'),
        ('province', 'Province'),
        ('country', 'Country'),
    )

    show_activity_choices = (
        ('male', 'male'),
        ('female', 'female'),
        ('both', 'both'),
    )

    title = models.CharField(max_length=255)
    level_code = models.CharField(max_length=12, choices=level_choices, default='coach')
    show_activity = models.CharField(max_length=12, choices=show_activity_choices, default='both')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name = _("Coach Level")
        verbose_name_plural = _("Coach Levels")


class Teacher(BaseUser):
    coach_levels = models.ManyToManyField(to=CoachLevel, related_name="coach_levels")

    class Meta:
        verbose_name = _("Coach")
        verbose_name_plural = _("Coaches")

    def save(self, *args, **kwargs):
        if self.id is None:
            self.password = make_password(self.password)
        super(Teacher, self).save(*args, **kwargs)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)
