from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as lt_

from apps.activity.static import gender_choice
from apps.common.helpers.media_filename_hash import MediaFileNameHash
from apps.user.models.base import BaseUser


class QuestionBaseCategory(models.Model):
    category_choice = (
        ('scientific', lt_('Scientific')),
        ('religious', lt_('religious'))
    )

    title = models.CharField(max_length=255)
    category_code = models.CharField(max_length=12, choices=category_choice, verbose_name=_("Category Code"))

    def __str__(self):
        return self.title

    def get_sub_categories(self):
        files = QuestionCategory.objects.filter(category=self)
        return files

    class Meta:
        verbose_name = _("Question Base Category")
        verbose_name_plural = _("Question Base Categories")


class QuestionCategory(models.Model):
    category = models.ForeignKey(to=QuestionBaseCategory, verbose_name=_("Question Base Category"))
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    gender = models.CharField(max_length=7, choices=gender_choice, verbose_name=_("Gender"), null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Question Category")
        verbose_name_plural = _("Question Categories")


class Question(models.Model):
    status_choice = (
        (1, 'New'),
        (2, 'Accepted'),
        (3, 'Cartable'),
        (4, 'Replied'),
        (5, 'Solved'),
    )

    type_choice = (
        ('question', 'question'),
        ('answer', 'answer'),
    )

    state_choice = (
        ('advisor', _('advisor')),
        ('expert', _('expert')),
        ('top_expert', _('top expert')),
    )

    state = models.CharField(default="advisor", max_length=12, choices=state_choice, verbose_name=_("State"))
    status = models.PositiveSmallIntegerField(default=1, choices=status_choice, verbose_name=_("Status"))

    type = models.CharField(max_length=12, choices=type_choice, verbose_name=_("Type"))
    body = models.TextField(default='', verbose_name=_("Body"))
    create_datetime = models.DateTimeField(auto_now_add=True, verbose_name=_("Create datetime"))

    subject = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Subject"))
    point = models.FloatField(default=None, null=True, blank=True, verbose_name=_("Point"))
    main_category = models.ForeignKey(QuestionBaseCategory, verbose_name=_("Main Category"), null=True)
    category = models.ForeignKey(QuestionCategory, default=None, blank=True, null=True, verbose_name=_("Category"))
    view_count = models.IntegerField(default=0, blank=True, null=True, verbose_name=_("View count"))
    creator = models.ForeignKey(User, verbose_name=_("Creator"), related_name="question_creator")
    has_in_faq = models.BooleanField(default=False, verbose_name=_("Has In Faq"))

    answer_to = models.ForeignKey(
        to="self", null=True, blank=True,
        default=None,
        related_name="question_answers",
        verbose_name=_("Answer to")
    )

    not_allow_user = models.ManyToManyField(
        User, blank=True,
        related_name='not_allow_user',
        verbose_name=_("not allow user")
    )

    gender = models.CharField(
        max_length=7, null=True, blank=True,
        choices=gender_choice,
        default=None,
        verbose_name=_("Gender")
    )

    def __str__(self):
        return self.subject if self.subject else ""

    def get_answers(self):
        answers = Question.objects.filter(answer_to=self).order_by("id")
        return answers

    def get_last_answer(self):
        answers = list(Question.objects.filter(
            answer_to=self,
            type="answer"
        ).order_by('-create_datetime'))
        if answers:
            return answers[0]
        return False

    def get_category(self):
        response = None
        if self.category:
            sub_category = self.category
            parent_category = sub_category.category

            response = {
                "id": parent_category.id,
                "title": parent_category.title,
                "category_code": parent_category.category_code,
                "sub_category": {
                    "id": sub_category.id,
                    "title": sub_category.title
                }
            }

        return response

    def get_files(self):
        files = QuestionFile.objects.filter(question=self)
        return files

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.id is None:
            if self.type == 'question':
                self.point = 0
                self.view_count = 0

        return super(Question, self).save()

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")


class QuestionFile(models.Model):
    file = models.FileField(upload_to=MediaFileNameHash("files"), verbose_name=_("File"))
    uploader = models.ForeignKey(BaseUser, verbose_name=_("Uploader"), null=True, blank=True)
    uploader_ip = models.CharField(max_length=30, verbose_name=_("Uploader ip"), null=True, blank=True)
    is_question = models.BooleanField(default=True, verbose_name=_("Is question"))
    gender = models.CharField(
        max_length=7,
        choices=gender_choice,
        default=None,
        verbose_name=_("Gender"),
        null=True, blank=True
    )
    question = models.ForeignKey(to=Question, related_name="question_files")
    size = models.CharField(max_length=150, default="", blank=True, null=True)
    title = models.CharField(max_length=255, default="", blank=True, null=True)

    def file_link(self):
        return "<a href='/{0}' style='margin-right: 2%' download>{1}</a>".format(self.file.url, _("Download"))

    file_link.allow_tags = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.id is None:
            try:
                self.title = self.file.name.split("@")[0]
            except:
                pass
            self.size = self.file.size

        super(QuestionFile, self).save()

    def __str__(self):
        return self.title


class QuestionRejectHistory(models.Model):
    reject_datetime = models.DateTimeField(verbose_name=_("Reject datetime"))
    reject_by = models.ForeignKey(to=User, verbose_name=_("Reject by"))
    question = models.ForeignKey(to=Question, verbose_name=_("Question"))
    gender = models.CharField(max_length=7, choices=gender_choice, default=None, verbose_name=_("Gender"))

    class Meta:
        verbose_name = _("Question Reject History")
        verbose_name_plural = _("Question Reject Histories")


class ConversionsComment(models.Model):
    body = models.TextField(verbose_name=_("Body"))
    create_datetime = models.DateTimeField(auto_now=True, verbose_name=_("Create datetime"))
    question = models.ForeignKey(to=Question, verbose_name=_("Answer"))
    creator = models.ForeignKey(BaseUser, verbose_name=_("Advisor"), null=True)

    class Meta:
        verbose_name = _("Conversion Comment")
        verbose_name_plural = _("Conversion Comments")
