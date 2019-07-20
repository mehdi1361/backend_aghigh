from django.utils.functional import SimpleLazyObject
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
from rest_framework.exceptions import ValidationError


# from rest_framework.request from Request
class AuthenticationMiddlewareJWT(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        print(token)
        data = {'token': token}
        try:
            valid_data = VerifyJSONWebTokenSerializer().validate(data)
            user = valid_data['user']
            request.user = user
        except ValidationError as v:
            print("validation error", v)

        return self.get_response(request)
        # request.user = SimpleLazyObject(lambda: self.__class__.get_jwt_user(request))
        # if not request.user.is_authenticated:
        #     token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        #     print(token)
        #     data = {'token': token}
        #     try:
        #         valid_data = VerifyJSONWebTokenSerializer().validate(data)
        #         user = valid_data['user']
        #         request.user = user
        #     except ValidationError as v:
        #         print("validation error", v)
        #
        # return self.get_response(request)