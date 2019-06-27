from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _
from apps.common.helpers.media_filename_hash import MediaFileNameHash
from apps.league.models import School, County, Province, Camp
from apps.user.models.base import BaseUser
from scripts.get_video_information import get_video_duration

from django.db.models.signals import post_delete
from django.dispatch import receiver


class Announcement(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Announcement Title"))
    description = models.TextField(verbose_name=_("Announcement Description"))
    image = models.ImageField(
        upload_to=MediaFileNameHash("images"),
        default=None, verbose_name=_("Image"),
        null=True, blank=True
    )
    creator = models.ForeignKey(to=User, verbose_name=_("User"), null=True, blank=True)
    has_date = models.BooleanField(verbose_name=_("Has Date"), default=False)
    date = models.DateTimeField(verbose_name=_("Date"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    view_count = models.IntegerField(default=0)
    release_time = models.DateTimeField(verbose_name=_("Release Time"), null=True)

    def get_files(self):
        values = AnnouncementFile.objects.filter(announcement_id=self.id)
        return values

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Announcement")
        verbose_name_plural = _("Announcements")


# class AnnouncementVisit(models.Model):
#     """مدل هیستوری جایگزین شده و دیگر از این استفاده نمی شود"""
#     # استفاده نمی شود
#     announcement = models.ForeignKey(
#         to=Announcement,
#         verbose_name=_("Announcement"),
#         on_delete=models.CASCADE
#     )
#     user = models.ForeignKey(
#         to=BaseUser,
#         on_delete=models.CASCADE,
#         verbose_name=_("Base User")
#     )
#
#     class Meta:
#         unique_together = ('announcement', 'user')


class AnnouncementReceiver(models.Model):
    gender_choice = (
        ('female', _('female')),
        ('male', _('male')),
        ('both', _('both')),

    )
    user_type_choices = (
        ('student', _('Students')),
        ('coach', _('Coaches')),
        ('province', _('Province Coach')),
        ('county', _('County Coach')),
        ('camp', _('Camp Coach')),
        ('country', _('Countries')),
    )

    user_type = models.CharField(max_length=10, choices=user_type_choices, verbose_name=_("User Type Receiver"))
    province = models.ForeignKey(to=Province, verbose_name=_("Province"), null=True, blank=True)
    county = models.ForeignKey(to=County, verbose_name=_("County"), null=True, blank=True)
    camp = models.ForeignKey(to=Camp, verbose_name=_("Camp"), null=True, blank=True)
    school = models.ForeignKey(to=School, verbose_name=_("School"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_("Updated at"))
    announcement = models.ForeignKey(to=Announcement, related_name="announcement_receivers", on_delete=models.CASCADE)
    gender = models.CharField(
        max_length=10,
        choices=gender_choice,
        default="both",
        verbose_name=_("Gender")
    )

    class Meta:
        verbose_name = _("Announcement Receiver")
        verbose_name_plural = _("Announcement Receivers")


class AnnouncementSeenHistory(models.Model):
    user = models.ForeignKey(to=User, verbose_name=_("User"), null=True, blank=True)
    announcement = models.ForeignKey(to=Announcement, verbose_name=_("Announcement"), null=True, blank=True)
    seen_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_("Seen at"))

    class Meta:
        verbose_name = _("Announcement Seen History")
        verbose_name_plural = _("Announcement Seen History")
        unique_together = ('user', 'announcement')


class AnnouncementFile(models.Model):
    title = models.CharField(max_length=150, default="")
    file = models.FileField(upload_to=MediaFileNameHash("files"), default=None, verbose_name=_("File"))
    size = models.CharField(max_length=150, default="", blank=True, null=True)
    duration = models.TimeField(blank=True, null=True)
    announcement = models.ForeignKey(to=Announcement, related_name="announcement_files", on_delete=models.CASCADE)

    def file_link(self):
        return "<a href='/{0}' style='margin-right: 2%'>{1}</a>".format(self.file.url, _("Download"))

    file_link.allow_tags = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.id is None:
            try:
                self.title = self.file.name.split("@")[0]
            except:
                pass
            self.size = self.file.size

        super(AnnouncementFile, self).save()
        # get file format
        file_format = self.file.name.split(".")[-1].upper()
        if file_format in ['MP4', 'FLV', 'MOV', 'AVI', 'MPEG', 'WMV', '3GP', 'VOB', 'MPG', 'MP3', 'M4A', 'OGG', 'WMA']:
            # get duration for video
            self.duration = get_video_duration(self.file.path)
            super(AnnouncementFile, self).save()

    class Meta:
        verbose_name = _("Announcement File")
        verbose_name_plural = _("Announcement Files")


@receiver(post_delete, sender=Announcement)
def photo_announcement_delete_handler(sender, **kwargs):
    listingImage = kwargs['instance']
    if listingImage.image:
        storage, path = listingImage.image.storage, listingImage.image.path
        storage.delete(path)


@receiver(post_delete, sender=AnnouncementFile)
def file_announcement_delete_handler(sender, **kwargs):
    listingFile = kwargs['instance']
    if listingFile.file:
        storage, path = listingFile.file.storage, listingFile.file.path
        storage.delete(path)
