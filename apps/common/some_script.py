import datetime
import hashlib

from django.db.models import Sum, Avg, Q
from django.conf import settings
from apps.activity.models import (
    Activity,
    RateActivity,
    ActivityDailyReport,
    StudentDailyReport,
    ImageActivity, FileActivity, ActivityAdditionalFields)
from apps.announcements.models import Announcement
from apps.emtiaz.models import Param, SumActivityParam, ActivityComment, HistoryScore
from apps.notification.models import Notification
from scripts.get_video_information import get_video_duration
from apps.question.models.managment import FaqQuestion


class Script(object):
    # @staticmethod
    # def set_new_category_score():
    #     new_additional_field = {
    #         33: (729, 1129),
    #         35: (728, 1124),
    #         34: (726, 1119),
    #     }
    #     for id_cat, id_additional in new_additional_field.items():
    #         acts = Activity.objects.filter(category_id=id_cat)
    #         for act in acts:
    #             find = ActivityAdditionalFields.objects.filter(additional_field_id=id_additional[0], activity=act)
    #             if find.exists():
    #                 find.delete()
    #
    #             ActivityAdditionalFields(activity=act, status=True, value=id_additional[1], additional_field_id=id_additional[0]).save()

    @staticmethod
    def activity_emtiaz(activity_id=None):
        if not activity_id:
            activities = Activity.objects.filter(state="ACCEPT")
        else:
            activities = Activity.objects.filter(id=activity_id)

        for activity in activities:
            rates = RateActivity.objects.filter(activity_id=activity.id)

            aggregate = rates.aggregate(Avg('rate'), Sum('average_absolute'))

            activity.point_emtiaz = float(aggregate["rate__avg"] if aggregate["rate__avg"] is not None else 0)
            activity.point_emtiaz_sum = float(aggregate["average_absolute__sum"] if aggregate["average_absolute__sum"] is not None else 0)
            activity.rate_count = rates.count()

            activity.save()

    @staticmethod
    def remove_repeat_sum_activity(activity_id=None):
        if not activity_id:
            activities = Activity.objects.filter(state="ACCEPT")
        else:
            activities = Activity.objects.filter(id=activity_id)

        params = Param.objects.filter()
        for activity in activities:
            for param in params:
                try:
                    SumActivityParam.objects.get(activity_id=activity.id, param_id=param.id)
                except:
                    extra_act = SumActivityParam.objects.filter(activity_id=activity.id, param_id=param.id)[1:]
                    if extra_act:
                        print(activity.id)
                    for a in extra_act:
                        a.delete()

    @staticmethod
    def remove_add_comment_activity():
        comments = ActivityComment.objects.all().values('activity_id', 'sender_id').distinct()
        for comment in comments:
            activity_id = comment['activity_id']
            student_id = comment['sender_id']
            try:
                ActivityComment.objects.get(activity_id=activity_id, sender_id=student_id)
            except:
                print(student_id)
                extra_act = ActivityComment.objects.filter(activity_id=activity_id, sender_id=student_id).order_by('create_at')[1:]
                for a in extra_act:
                    a.delete()

    @staticmethod
    def remove_repeat_rate():
        rates = RateActivity.objects.all().values('activity_id', 'student_id').distinct()
        for rate in rates:
            activity_id = rate['activity_id']
            student_id = rate['student_id']
            try:
                RateActivity.objects.get(activity_id=activity_id, student_id=student_id)
            except:
                print(activity_id)
                extra_act = RateActivity.objects.filter(activity_id=activity_id, student_id=student_id).order_by('created_at')[1:]
                for a in extra_act:
                    a.delete()

    # @staticmethod
    # def remove_repeat_announcement_visit():
    #     announcements = AnnouncementVisit.objects.all().values("announcement_id", "user_id").distinct()
    #     for announcement in announcements:
    #         announcement_id = announcement['announcement_id']
    #         user_id = announcement['user_id']
    #         try:
    #             AnnouncementVisit.objects.get(announcement_id=announcement_id, user_id=user_id)
    #         except:
    #             print(announcement_id)
    #             extra_act = AnnouncementVisit.objects.filter(announcement_id=announcement_id, user_id=user_id).order_by('id')[1:]
    #             for a in extra_act:
    #                 a.delete()

    @staticmethod
    def daily_activity_point_change(database='default'):
        today = datetime.datetime.today()
        activities = Activity.objects.using(database).filter(state="ACCEPT")
        ActivityDailyReport.objects.using(database).all().delete()
        for activity in activities:
            a_c = activity.accepted_at.date()
            while a_c < today.date():
                date_old = datetime.date(year=a_c.year, month=a_c.month, day=a_c.day) - datetime.timedelta(days=1)
                date_now = datetime.date(year=a_c.year, month=a_c.month, day=a_c.day) + datetime.timedelta(days=1)
                daily_report = ActivityDailyReport.objects.using(database).filter(activity_id=int(activity.id), date=a_c)

                aggregate = RateActivity.objects.using(database).filter(
                    activity_id=activity.id,
                    created_at__gt=date_old,
                    created_at__lt=date_now
                ).aggregate(Sum('average_absolute'))["average_absolute__sum"]

                average_absolute = aggregate if aggregate is not None else 0
                if daily_report.exists():
                    daily_report.update(point=average_absolute)

                else:
                    ActivityDailyReport(
                        date=a_c,
                        point=average_absolute,
                        activity_id=int(activity.id)
                    ).save(using=database)
                a_c += datetime.timedelta(days=1)

    @staticmethod
    def daily_student_point_change(database='default'):
        StudentDailyReport.objects.using(database).all().delete()
        rates = RateActivity.objects.using(database).all()

        for rate in rates:
            try:
                student = StudentDailyReport.objects.using(database).get(
                    date=rate.created_at.date(),
                    student_id=rate.student_id
                )
                student.point = student.point + rate.point_student
                student.save()

            except:
                StudentDailyReport(
                    date=rate.created_at.date(),
                    student=rate.student,
                    point=rate.point_student
                ).save(using=database)

    @staticmethod
    def set_average_absolute():
        from apps.emtiaz.models import ActivityComment, ParamActivityComment
        from apps.activity.models import RateActivity

        comment = ActivityComment.objects.all()
        for act in comment:
            try:
                rate = RateActivity.objects.get(student_id=act.sender.id, activity_id=act.activity.id)
            except:
                continue

            student_comment = ParamActivityComment.objects.filter(
                ~Q(value=0),
                activity_comment__sender_id=act.sender.id,
                activity_comment__activity_id=act.activity.id,
            ).aggregate(Avg('value'))['value__avg']

            if student_comment and student_comment != 0:
                average_absolute = (student_comment + rate.rate) / 2

            else:
                average_absolute = rate.rate

            rate.average_absolute = average_absolute
            rate.save()

    @staticmethod
    def remove_viewer_repeat(database='default'):
        from apps.activity.models import ActivityState

        viewers = ActivityState.objects.using(database).all().values('activity_id', 'viewer_id').distinct()

        for view in viewers:
            activity_id = view['activity_id']
            viewer_id = view['viewer_id']
            try:
                ActivityState.objects.using(database).get(activity_id=activity_id, viewer_id=viewer_id)
            except:
                print(viewer_id)
                extra_act = ActivityState.objects.using(database).filter(activity_id=activity_id, viewer_id=viewer_id).order_by('created_at')[1:]
                for a in extra_act:
                    a.delete()

    @staticmethod
    def remove_announcement_seen_history_repeat(database='default'):
        from apps.announcements.models import AnnouncementSeenHistory
        viewers = AnnouncementSeenHistory.objects.using(database).all().values('user_id', 'announcement_id').distinct()

        for view in viewers:
            user_id = view['user_id']
            announcement_id = view['announcement_id']
            try:
                AnnouncementSeenHistory.objects.using(database).get(
                    user_id=user_id,
                    announcement_id=announcement_id
                )
            except:
                print(announcement_id)
                extra_act = AnnouncementSeenHistory.objects.using(database).filter(
                    user_id=user_id,
                    announcement_id=announcement_id
                ).order_by('seen_at')[1:]
                for a in extra_act:
                    a.delete()

    @staticmethod
    def activity_comments_counter():
        activities = Activity.objects.all()

        for item in activities:
            comments_count = ActivityComment.objects.filter(activity=item).count()
            item.comments_count = comments_count
            item.save()

    @staticmethod
    def cleaned_database():
        Activity.objects.all().delete()
        Announcement.objects.all().delete()
        HistoryScore.objects.all().delete()
        Notification.objects.all().delete()
        StudentDailyReport.objects.all().delete()

        from apps.user.models.student import ActivationBySmsCode
        ActivationBySmsCode.objects.all().delete()

        from apps.league.models import School
        schools = School.objects.all()
        for item in schools:
            item.point = 0
            item.rank = 0
            item.county_rank = 0
            item.province_rank = 0
            item.save()

        from apps.user.models.base import BaseUser
        users = BaseUser.objects.filter(user_is_test=False)
        for user in users:
            user.is_active = False
            user.save()

    @staticmethod
    def added_durations_to_files_shop():
        from apps.shop.models import ProductFile
        files = ProductFile.objects.all()
        for file in files:
            file_format = file.file.name.split(".")[-1].upper()
            if file_format in ['MP4', 'FLV', 'MOV', 'AVI', 'MPEG', 'WMV', '3GP', 'VOB', 'MPG', 'MP3', 'M4A', 'OGG', 'WMA']:
                # get duration for video or audio
                file.duration = get_video_duration(file.file.path)
                print(file.duration)
                file.save()

    @staticmethod
    def make_all_faqs_accepted():
        faqs = FaqQuestion.objects.all()
        for faq in faqs:
            faq.is_accepted = True
            faq.save()


def server_public_url(image, size=None):
    image_split = image.split(".")
    _image = size + "." + image_split.pop(-1)
    image = ""
    for i in image_split:
        image += i + "."
    return image + _image


def confirm_all_data_activity():
    print("start change state image and file and additional fields")
    now_date = datetime.datetime.now()
    pre_month = now_date - datetime.timedelta(weeks=5)
    for activity in Activity.objects.filter(state="ACCEPT", accepted_at__gt=pre_month):

        # confirm images
        images = ImageActivity.objects.filter(activity=activity)
        for image in images:
            image.status = True
            image.save()

        # confirm files
        files = FileActivity.objects.filter(activity=activity)
        for file in files:
            file.status = True
            file.save()

        # confirm additional fields
        additional_fields = ActivityAdditionalFields.objects.filter(activity=activity)
        for add in additional_fields:
            add.status = True
            add.save()
    print("end change state image and file and additional fields")


def baghery_encode(data):
    user_name = hashlib.md5(data.encode()).hexdigest()
    data = user_name[0:8] + "-" + user_name[8:12] + "-" + user_name[12:16] + "-" + user_name[16:20] + "-" + user_name[20:32]

    return data
