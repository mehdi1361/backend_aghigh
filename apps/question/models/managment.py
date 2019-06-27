from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as lt_

from apps.user.models.advisor import Advisor
from apps.question.models.questions import QuestionCategory, Question, QuestionBaseCategory
from apps.activity.static import gender_choice


class AdvisorQuestion(models.Model):
    status_choice = (
        ('answered', lt_('Answered')),
        ('waiting', lt_('Waiting'))
    )

    advisor = models.ForeignKey(Advisor, verbose_name=_("Advisor"))
    question = models.ForeignKey(Question, related_name="advisor_question", verbose_name=_("Question"))
    created_at = models.DateTimeField(auto_now=True, verbose_name=_("Created time"))
    status = models.CharField(max_length=13, choices=status_choice, verbose_name=_("Status"))

    class Mata:
        verbose_name = _("Advisor Work Table")
        # verbose_name = "تیسنبیتس نب تی بنیت"
        verbose_name_plural = _("Advisor Work Tables")
        # verbose_name_plural = "سیابت یسن"


class FaqQuestion(models.Model):
    subject = models.CharField(max_length=255, verbose_name=_("Subject"))
    question = models.TextField(verbose_name=_("Question"))
    answer = models.TextField(verbose_name=_("Answer"))
    create_datetime = models.DateTimeField(auto_now=True, verbose_name=_("Create DateTime"))
    category = models.ForeignKey(to=QuestionBaseCategory, verbose_name=_("Question Base Category"))
    sub_category = models.ForeignKey(
        QuestionCategory,
        default=None, blank=True, null=True,
        verbose_name=_("Sub Category")
    )

    gender = models.CharField(max_length=7, choices=gender_choice, verbose_name=_("Gender"))
    point = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    is_accepted = models.BooleanField(default=False, verbose_name=_("Is Accepted"))
    related_question_id = models.PositiveSmallIntegerField(blank=True, null=True)

    create_by = models.ForeignKey(
        Advisor,
        null=True,
        related_name="Advisor",
        verbose_name=_("Faq Question Creator")
    )

    class Meta:
        verbose_name = _("Faq Question")
        verbose_name_plural = _("Faq Questions")

