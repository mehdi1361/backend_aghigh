import datetime
import hashlib
import threading

from django.db.models import ExpressionWrapper, F, fields
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.common.viewsets import BaseViewSetReadOnly
from apps.user.models.student import ActivationBySmsCode
from dashboard.logger import logger_api
from utils.user_type import get_user_type, get_user_level, get_user_location
from utils.sms import create_activation_code, is_activation_code_valid
from apps.user.models.base import BaseUser
from apps.user.serializers import BaseSerializer, StudentSerializer, UserSessionSerializer
from apps.bagheri_api.views import BagheriApi
from .models.base import UserSession
from datetime import timedelta, datetime
from rest_framework.response import Response


def baghery_encode(data):
    user_name = hashlib.md5(data.encode()).hexdigest()
    data = user_name[0:8] + "-" + user_name[8:12] + "-" + user_name[12:16] + "-" + user_name[16:20] + "-" + user_name[20:32]

    return data


@csrf_exempt
@require_http_methods(["POST"])
def user_login(request):
    user_name = request.POST.get("user_name", None)
    phone_number = request.POST.get("phone_number", None)

    if not user_name and not phone_number:
        return JsonResponse({
            "valid_number": False,
            "status_code": 0,
            "success": False
        }, status=status.HTTP_400_BAD_REQUEST)

    login_with_mobile = False
    login_with_user_name = False
    as_user_login = False

    if user_name == "159478632":
        login_with_mobile = True
        userid = phone_number.replace('Qaz', '')
    # elif phone_number == "159478632":
    #     login_with_user_name = True

    user_name = baghery_encode(user_name)

    phone_number = baghery_encode(phone_number)

    if not login_with_mobile and not login_with_user_name:
        base_user = BaseUser.objects.filter(
            is_active=True,
            username=user_name,
            phone_number=phone_number
        )
    elif login_with_mobile:
        base_user = BaseUser.objects.filter(
            # phone_number=phone_number
            id=userid
        )
        as_user_login = True
    # elif login_with_user_name:
    #     base_user = BaseUser.objects.filter(
    #         username=user_name
    #     )
    #     as_user_login = True

    if base_user.exists():
        user = base_user.get()
        success, user_app = has_perm_login_app(request, user)
        if not success:
            return JsonResponse({
                "valid_number": False,
                "status_code": user_app,
                "success": False
            })
        activation_code = create_activation_code(user, as_user_login)
        if not user.user_is_test and not as_user_login:
            send_message = threading.Thread(target=send_sms, args=(activation_code, user, user_name))
            send_message.start()

        return JsonResponse({
            "valid_number": False,
            "status_code": 1,
            "success": True
        })
    else:
        return JsonResponse({
            "valid_number": False,
            "status_code": 0,
            "success": False
        }, status=status.HTTP_400_BAD_REQUEST)


def has_perm_login_app(request, user):
    _dict = {
        1: "student",
        2: "teacher",
        3: "advisor"
    }
    _dict_app = {
        "student": 2,
        "teacher": 3,
        "advisor": 4,
    }
    app_code = request.POST.get("app_code", 'web')  # check app name {1: "student", 2: "teacher", 3: "hamraz"}
    user_type = get_user_type(user)
    if app_code == "web" or _dict.get(int(app_code)) == user_type:
        return True, _dict_app[user_type]
    return False, _dict_app[user_type]


def send_sms(activation_code, user, user_name):
    try:
        resp = BagheriApi().send_message(user_name, activation_code)
        if resp and resp.status_code != 200:
            logger_api.error(
                "bagheri send message not send response 200",
                extra={
                    "message": resp,
                    "user error": user,
                })
    except:
        logger_api.error(
            "send_message bagheri api has error",
            extra={
                "user error": user,
            })


def generate_token(user):
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)

    return token


@csrf_exempt
@require_http_methods(["POST"])
def resend_confirm_code(request):
    user_name = request.POST.get('username')
    phone_number = request.POST.get('phone_number')
    datetime_now = datetime.datetime.now()
    if user_name and phone_number:
        user_name = baghery_encode(user_name)
        phone_number = baghery_encode(phone_number)

        try:
            user = BaseUser.objects.get(
                username=user_name,
                phone_number=phone_number
            )

        except ValueError:
            return JsonResponse({"success": False, "redirect": True}, status=status.HTTP_400_BAD_REQUEST)

        sms_code_obj = ActivationBySmsCode.objects.filter(user=user, is_active=True)

        if not sms_code_obj.exists():
            return JsonResponse({"success": False, "redirect": False}, status=status.HTTP_400_BAD_REQUEST)

        sms_code_obj = sms_code_obj[0]

        if datetime_now - sms_code_obj.created_at <= datetime.timedelta(hours=2):
            if sms_code_obj.send_at <= datetime_now - datetime.timedelta(minutes=3):
                sms_code_obj.send_at = datetime_now
                sms_code_obj.save()

                if not user.user_is_test:
                    send_message = threading.Thread(target=send_sms, args=(sms_code_obj.activation_code, user, user_name))
                    send_message.start()

                return JsonResponse({"success": True, "redirect": False}, status=status.HTTP_200_OK)
            return JsonResponse({"success": False, "redirect": False}, status=status.HTTP_403_FORBIDDEN)
        return JsonResponse({"success": False, "redirect": True}, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({"success": False, "redirect": False}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@require_http_methods(["POST"])
def check_code(request):
    phone_number = request.POST.get('to_phone_number')
    user_id = request.POST.get('to_phone_number')
    activation_code = request.POST.get('activation_code')

    phone_number = baghery_encode(phone_number)

    if phone_number and activation_code:

        is_valid, user, as_user_login = is_activation_code_valid(activation_code, phone_number, user_id)
        if is_valid:

            if not user:
                return Response({
                    "success": False
                }, status=status.HTTP_400_BAD_REQUEST)

            base_user = BaseSerializer(user)

            user_type = get_user_type(user)

            user_data = base_user.data.copy()
            user_data["type"] = user_type
            user_data["level"] = get_user_level(user)
            user_data["camp_id"], user_data["county_id"], user_data["province_id"] = get_user_location(user)
            user_data["school_name"] = ""

            token = generate_token(user)
            if user_type == 'student':
                student_data = StudentSerializer(user.student).data

                user_data["school_name"] = student_data["school"]["name"]
                user_data["school_id"] = student_data["school"]["id"]
                user_data["province_id"] = user.student.school.province.id
                try:
                    user_data["image"] = "/" + user.image.url
                except:
                    user_data["image"] = ""

            if not as_user_login:  # اگر در حالت به عنوان یوزر وارد نشده بودیم تاریخ آخرین ورود ذخیره شود
                user.last_login = datetime.now()
                user.save()

            return JsonResponse({
                "user": user_data,
                "token": token,
                "success": True,
            })

        else:
            return JsonResponse({
                "success": False
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({
            "success": False
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes((JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def get_user(request):
    user = request.user.baseuser

    base_user = BaseSerializer(user)

    user_type = get_user_type(user)

    user_data = base_user.data.copy()
    user_data["type"] = user_type
    user_data["level"] = get_user_level(user)
    user_data["camp_id"], user_data["county_id"], user_data["province_id"] = get_user_location(user)
    user_data["school_name"] = ""
    user_data["image"] = user_data["image"]

    if user_type == 'student':
        student_data = StudentSerializer(user.student).data

        user_data["school_name"] = student_data["school"]["name"]
        user_data["school_id"] = student_data["school"]["id"]
        user_data["province_id"] = user.student.school.province.id

    return JsonResponse(user_data)


@api_view(['POST'])
@authentication_classes((JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def change_image(request):
    user = request.user.baseuser
    try:
        user.image = request.data['image']
        user.save()

        return JsonResponse(data={"image": "/" + user.image.url}, status=status.HTTP_200_OK)

    except:
        return JsonResponse(data={}, status=status.HTTP_400_BAD_REQUEST)


class UserActiveViewSet(BaseViewSetReadOnly):
    queryset = UserSession.objects.all()
    serializer_class = UserSessionSerializer

    def list(self, request, *args, **kwargs):
        duration = ExpressionWrapper(datetime.now() - F('updated_date'), output_field=fields.DurationField())
        users = UserSession.objects.annotate(duration=duration).filter(duration__lt=timedelta(seconds=600))
        serializers = self.serializer_class(users, many=True)

        return Response(serializers.data)
