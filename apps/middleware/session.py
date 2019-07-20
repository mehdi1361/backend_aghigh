from datetime import datetime
from django.http import HttpResponse
from apps.user.models.base import UserSession


class LogActivation(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        pass
        # if request.user.username != "":
        #     user, create = UserSession.objects.get_or_create(
        #         user_name=request.user.username,
        #         defaults={"updated_date": datetime.now()}
        #     )
        #     if not create:
        #         user.updated_date = datetime.now()
        #         user.save()
        return self.get_response(request)

    # def process_exception(self, request, exception):
    #     return HttpResponse("in exception")

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.username != "":
            user, create = UserSession.objects.get_or_create(
                user_name=request.user.username,
                defaults={
                    "updated_date": datetime.now(),
                    "last_login_date": request.user.last_login
                }
            )
            if not create:
                user.updated_date = datetime.now()
                user.save()