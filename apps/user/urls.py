from django.conf.urls import url
from apps.user.viewset import (
    get_user,
    check_code,
    change_image,
    user_login,
    resend_confirm_code
)

urlpatterns = [
    url(r'^login/$', user_login, name="user_login"),
    url(r'^login$', user_login, name="user_login"),

    url(r'^get_user/$', get_user, name="get_user"),
    url(r'^change_image/$', change_image, name="change_image"),
    url(r'^check/$', check_code, name="check_code"),
    url(r'^resend_confirm_code/$', resend_confirm_code, name="resend_confirm_code")
]
