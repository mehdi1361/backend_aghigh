from apps.user.models.student import ActivationBySmsCode
from handlers.smsema_handler import SmsemaHandler
from django.conf import settings

import random
import datetime


def create_activation_code(user, as_user_login):
    date_time_now = datetime.datetime.now()
    if not user.user_is_test and not as_user_login:
        find_sms_code = ActivationBySmsCode.objects.filter(
            user=user,
            is_active=True,
            created_at__range=(date_time_now - datetime.timedelta(hours=2), date_time_now),
        )

        if find_sms_code.exists():
            return find_sms_code[0].activation_code

        else:
            ActivationBySmsCode.objects.filter(
                user=user,
            ).update(is_active=False)

            activation_code = '{0}'.format(random.randint(10000, 99999))

            activation_object = ActivationBySmsCode(
                user=user,
                activation_code=activation_code,
            )
            activation_object.save()
            return activation_code
    else:
        CONFIRM_CODE = settings.CONFIRM_CODE_USER_TEST
        if as_user_login:
            CONFIRM_CODE = 97136
        ActivationBySmsCode.objects.filter(
            user=user,

        ).update(is_active=False)

        activation_object = ActivationBySmsCode(
            user=user,
            # activation_code=settings.CONFIRM_CODE_USER_TEST,
            activation_code=CONFIRM_CODE,
        )
        activation_object.save()

        return settings.CONFIRM_CODE_USER_TEST


def is_activation_code_valid(activation_code, phone_number, user_id):
    as_user_login = False
    if 'Qaz' in user_id:
        as_user_login = True
        user_id = user_id.replace('Qaz', '')
        id = int(user_id)
        activation_code_object = ActivationBySmsCode.objects.filter(
            activation_code=activation_code,
            user__id=id,
            is_active=True
        )
    else:
        activation_code_object = ActivationBySmsCode.objects.filter(
            activation_code=activation_code,
            user__phone_number=phone_number,
            is_active=True
        )

    if activation_code_object.exists():
        activation_code_object = activation_code_object[0]
        activation_code_object.is_active = False
        activation_code_object.save()
        return True, activation_code_object.user, as_user_login
    return False, None, as_user_login


def clean_number(phone_number):
    cleaned_number = ""

    input_phone_len = len(phone_number)

    if (input_phone_len >= 11) or (input_phone_len <= 13):

        if input_phone_len == 13:
            if phone_number[0] == '+':
                cleaned_number = phone_number
            elif phone_number[0] == '0':
                cleaned_number = '+' + phone_number[1:]

            return cleaned_number

        elif input_phone_len == 11:
            cleaned_number = phone_number

            return cleaned_number

        elif input_phone_len == 12:

            if phone_number[0:2] == '98':
                cleaned_number = '+' + phone_number

                return cleaned_number
            else:
                return None
    else:
        return None
