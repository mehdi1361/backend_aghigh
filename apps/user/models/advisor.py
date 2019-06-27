from django.contrib.auth.hashers import make_password
from django.db import models
from django.utils.translation import ugettext as _
from apps.question.models.questions import QuestionBaseCategory, QuestionCategory
from apps.user.models.base import BaseUser


class AdvisorLevel(models.Model):
    level_choices = (
        ('advisor', _('advisor')),
        ('expert', _('expert')),
        ('top_expert', _('top expert'))
    )

    title = models.CharField(max_length=255)
    level_code = models.CharField(max_length=12, choices=level_choices, default='coach')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Advisor Level")
        verbose_name_plural = _("Advisor Levels")


class Advisor(BaseUser):

    levels = models.ManyToManyField(to=AdvisorLevel)
    category = models.ForeignKey(to=QuestionBaseCategory, verbose_name=_("Question Base Category"), null=True)
    sub_categories = models.ManyToManyField(QuestionCategory, blank=True, verbose_name=_("Sub Category"))

    def __str__(self):
        return "%s  %s" % (self.first_name, self.last_name)

    class Meta:
        verbose_name = _("Advisor")
        verbose_name_plural = _("Advisor")

    def save(self, *args, **kwargs):
        if self.id is None:
            self.password = make_password(self.password)
        super(Advisor, self).save(*args, **kwargs)
