from pyfcm import FCMNotification
from django.conf import settings

from apps.notification.viewset import calculate_notification_count_set_cache
from dashboard.logger import logger_v1
from apps.user.models.student import Student
from apps.notification.models import FcmTokenUser
from apps.notification.models import Notification
from apps.league.models import School


def send_notification_student_activity(activity):
    push_service = FCMNotification(api_key=settings.CONFIG_FCM_STUDENT["api_key"])

    message_title = False
    message_body = ""
    action = "open_activity"
    if activity.state == "ACCEPT":
        message_title = "فعالیت شما تایید شد."
        message_body = "فعالیت شما با عنوان " + activity.title + " تایید شد"

    elif activity.state == "SHE":
        message_title = "فعالیت شما نیاز به ویرایش دارد."
        message_body = "فعالیت شما با عنوان " + activity.title + " نیاز به ویرایش دارد."
        action = "edit_activity"

    user = FcmTokenUser.objects.filter(user_id=activity.student_id)
    activity_images = activity.get_images()

    data_message = {
        "title": message_title,
        "body": message_body,
        "action": action,
        "activity_id": activity.id,
        "activity_image_url": activity_images[0].image.url
    }

    save_notification(activity.student_id, message_title, message_body, data_message)

    if user and message_title:

        tokens = user.get()
        registration_ids = []

        if tokens.mobile_token:
            registration_ids.append(tokens.mobile_token)

        if tokens.web_token:
            registration_ids.append(tokens.web_token)

        valid_registration_ids = push_service.clean_registration_ids(registration_ids)

        result = push_service.notify_multiple_devices(
            registration_ids=valid_registration_ids,
            data_message=data_message
        )
        logger_v1.info("send_notification_student_activity", extra={
            "detail": {
                "response": result
            }
        })

        return result


def send_notification_teacher_activity(activity):
    push_service = FCMNotification(api_key=settings.CONFIG_FCM_TEACHER["api_key"])

    message_title = False
    message_body = ""
    if activity.state == "NEW":
        message_title = "فعالیت جدید."
        try:
            school_name = School.objects.filter(id=activity.school_id).get().name
            message_body = "فعالیت جدید از مدرسه " + school_name
        except:
            pass

    elif activity.state == "SHR":
        message_title = "فعالیت دوباره بررسی شود."
        message_body = "فعالیت با عنوان " + activity.title + " نیاز به بررسی دارد."

    student = Student.objects.filter(id=activity.student_id).select_related("school")
    if student and message_title:
        student = student.get()
        activity_images = activity.get_images()

        data_message = {
            "title": message_title,
            "body": message_body,
            "action": "check_activity",
            "activity_id": activity.id,
            "activity_image_url": activity_images[0].image.url
        }
        user = FcmTokenUser.objects.filter(user_id=student.school.teacher_id)
        save_notification(student.school.teacher_id, message_title, message_body, data_message)

        if user and message_title:
            registration_ids = []
            tokens = user.get()
            if tokens.mobile_token:
                registration_ids.append(tokens.mobile_token)

            if tokens.web_token:
                registration_ids.append(tokens.web_token)

            valid_registration_ids = push_service.clean_registration_ids(registration_ids)

            result = push_service.notify_multiple_devices(
                registration_ids=valid_registration_ids,
                data_message=data_message
            )

            logger_v1.info("send_notification_teacher_activity", extra={
                "detail": {
                    "response": result
                }
            })

            return result


def send_notification_for_new_answer_to_student(question_id, creator_id):
    push_service = FCMNotification(api_key=settings.CONFIG_FCM_STUDENT["api_key"])

    message_title = "پاسخ جدیدی به سوال شما داده شد."
    message_body = ""

    data_message = {
        "title": message_title,
        "body": message_body,
        "action": "new_answer",
        "question_id": question_id
    }
    user = FcmTokenUser.objects.filter(user_id=creator_id)
    save_notification(creator_id, message_title, message_body, data_message)

    if user.exists():
        registration_ids = []
        tokens = user.get()
        if tokens.mobile_token:
            registration_ids.append(tokens.mobile_token)

        if tokens.web_token:
            registration_ids.append(tokens.web_token)

        valid_registration_ids = push_service.clean_registration_ids(registration_ids)

        result = push_service.notify_multiple_devices(
            registration_ids=valid_registration_ids,
            data_message=data_message
        )

        logger_v1.info("send_notification_for_new_answer", extra={
            "detail": {
                "response": result
            }
        })

        return result


def send_notification_for_new_answer_to_teacher(question_id, creator_id):
    push_service = FCMNotification(api_key=settings.CONFIG_FCM_STUDENT["api_key"])

    message_title = "پاسخ جدیدی به جواب شما داده شد."
    message_body = ""

    data_message = {
        "title": message_title,
        "body": message_body,
        "action": "new_answer",
        "question_id": question_id
    }
    user = FcmTokenUser.objects.filter(user_id=creator_id)
    save_notification(creator_id, message_title, message_body, data_message)

    if user.exists():
        registration_ids = []
        tokens = user.get()
        if tokens.mobile_token:
            registration_ids.append(tokens.mobile_token)

        if tokens.web_token:
            registration_ids.append(tokens.web_token)

        valid_registration_ids = push_service.clean_registration_ids(registration_ids)

        result = push_service.notify_multiple_devices(
            registration_ids=valid_registration_ids,
            data_message=data_message
        )

        logger_v1.info("send_notification_for_new_answer", extra={
            "detail": {
                "response": result
            }
        })

        return result


def save_notification(user_id, title, body, body_action=None):
    notify = Notification()
    notify.title = title
    notify.body = body
    notify.send_to_id = user_id
    if body_action:
        if body_action["action"] == "check_activity" or body_action["action"] == "edit_activity" or body_action["action"] == "open_activity":
            Notification.objects.filter(body_action__activity_id=body_action["activity_id"]).update(seen=True)

        if body_action["action"] == "new_answer":
            Notification.objects.filter(body_action__question_id=body_action["question_id"]).update(seen=True)

        notify.body_action = body_action

    notify.save()
    # بروزرسانی تعداد اعلانات این یوزر
    calculate_notification_count_set_cache(user_id)
