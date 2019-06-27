from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext as _
from apps.activity.models import Activity
from apps.user.models import student
from apps.league.models import School


class Param(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title Param"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Param")
        verbose_name_plural = _("Param")


class ActivityComment(models.Model):
    activity = models.ForeignKey(to=Activity, verbose_name=_("activity"), related_name="activity_comment")
    create_at = models.DateTimeField(auto_now=True)
    sender = models.ForeignKey(to=student.Student, null=True)
    comment = models.TextField(verbose_name=_("Comment"), null=True, blank=True)
    status = models.BooleanField(verbose_name=_("status"), default=False)

    def get_param(self):
        params = ParamActivityComment.objects.filter(activity_comment_id=self.id) \
            .select_related('param')
        return params

    class Meta:
        verbose_name = _("Activity Comment")
        verbose_name_plural = _("Activity Comments")
        unique_together = ("activity", 'sender')

    def __str__(self):
        return str(self.id)


class ParamActivityComment(models.Model):
    activity_comment = models.ForeignKey(to=ActivityComment, verbose_name=_("activity comment"))
    param = models.ForeignKey(to=Param, verbose_name=_("param"))
    value = models.PositiveIntegerField(verbose_name=_("value"), default=0)

    class Meta:
        verbose_name = _("Param Activity Comment")
        verbose_name_plural = _("Param Activity Comments")


class SumActivityParam(models.Model):
    activity = models.ForeignKey(to=Activity)
    param = models.ForeignKey(to=Param, verbose_name=_("Param"))
    sum = models.IntegerField(verbose_name=_("Sum"))
    count = models.IntegerField(verbose_name=_("Count"))

    class Meta:
        verbose_name = _("Sum Activity Param")
        verbose_name_plural = _("Sum Activity Params")


class HistoryScore(models.Model):
    school = models.ForeignKey(to=School)
    g1 = models.IntegerField(verbose_name=_("g1"), help_text="system point")
    g2 = models.IntegerField(verbose_name=_("g2"), help_text="evaluation activity and their relationship")
    g3 = models.IntegerField(verbose_name=_("g3"), help_text="point student of activity")
    g4 = models.IntegerField(verbose_name=_("g4"), help_text="acting points on the site")
    percent = models.IntegerField(verbose_name=_("percent"), help_text="int(math.ceil(((g1 + g2 + g4) * MINIMUM_PERCENTAGE_POINT) / 100))")

    final_point = models.IntegerField(verbose_name=_("final_point"), help_text="g1 + g2 + min(g3, _percent) + g4", default=0)
    count_all_activity = models.IntegerField(verbose_name=_("count_all_activity"), default=0)
    count_best_activity = models.IntegerField(verbose_name=_("count_best_activity"), default=0)

    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("History Score")
        verbose_name_plural = _("History Score")


def add_comments_count(sender, instance, created, **kwargs):
    if created:
        activity_obj = instance.activity
        activity_obj.comments_count += 1
        instance.activity.save()

post_save.connect(add_comments_count, sender=ActivityComment)
