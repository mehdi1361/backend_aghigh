from django.db import models
from apps.activity import static
from apps.common.models import TimeStampedModel
from apps.user.models.teacher import Teacher
from django.utils.translation import ugettext as _
from apps.common.helpers.media_filename_hash import MediaFileNameHash


class Department(models.Model):
    title = models.CharField(max_length=150, verbose_name=_("Title"))
    slug = models.CharField(max_length=150, verbose_name=_("Slug"), null=True, blank=True)
    max_point = models.PositiveIntegerField(verbose_name=_("Max Point"), default=500)
    max_count_activity = models.PositiveIntegerField(verbose_name=_("Max Count Activity"), default=0)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Department")


class Province(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    slug = models.CharField(max_length=255, verbose_name=_("Slug"))
    code = models.CharField(max_length=50, verbose_name=_("Code"))
    coaches = models.ManyToManyField(to=Teacher, verbose_name=_("Coaches"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Province")
        verbose_name_plural = _("Provinces")


class County(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    slug = models.CharField(max_length=255, verbose_name=_("Slug"))
    code = models.CharField(max_length=50, verbose_name=_("Code"))
    province = models.ForeignKey(to=Province, verbose_name=_("Province"), null=True)
    coach = models.ForeignKey(to=Teacher, verbose_name=_("Coach"), null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("County")
        verbose_name_plural = _("Counties")


class Camp(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    slug = models.CharField(max_length=255, verbose_name=_("Slug"))
    code = models.CharField(max_length=50, verbose_name=_("Code"))
    coach = models.ForeignKey(to=Teacher, verbose_name=_("Coach"))
    county = models.ForeignKey(to=County, verbose_name=_("Camp County"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Camp")
        verbose_name_plural = _("Camps")


class School(TimeStampedModel):
    name = models.CharField(max_length=45, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=static.gender_choice, default=None, null=True, blank=True)
    active = models.BooleanField(default=False)
    teacher = models.ForeignKey(to=Teacher)
    code_bagheri = models.CharField(max_length=45)

    camp = models.ForeignKey(to=Camp, verbose_name=_("Camp"), null=True, blank=True)
    county = models.ForeignKey(to=County, verbose_name=_("County"))
    province = models.ForeignKey(to=Province, verbose_name=_("Province"))

    voters = models.PositiveIntegerField(default=0, verbose_name=_("Voters"))
    image = models.ImageField(
        upload_to=MediaFileNameHash("images"),
        verbose_name=_("rank"),
        null=True,
        blank=True
    )

    student_count = models.PositiveIntegerField(verbose_name=_("Student Count"), default=0)
    anjoman_count = models.PositiveIntegerField(verbose_name=_("Anjoman Count"), default=0)
    point = models.PositiveIntegerField(default=0, verbose_name=_("Point"))
    rank = models.PositiveIntegerField(default=0, verbose_name=_("Rank"))
    province_rank = models.PositiveIntegerField(default=0, verbose_name=_("Province Rank"))
    county_rank = models.PositiveIntegerField(default=0, verbose_name=_("County Rank"))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _("School")
        verbose_name_plural = _("School")
