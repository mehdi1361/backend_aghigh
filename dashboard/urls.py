from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_jwt.views import obtain_jwt_token
# from silk.profiling.profiler import silk_profile

from dashboard.router import api_v1_router, api_v2_router
from rest_framework_jwt.views import refresh_jwt_token
from dashboard.logger import logger_v1

admin.site.site_header = 'Aghigh admin'
admin.site.site_title = 'Aghigh admin'
admin.site.index_title = 'Aghigh administration'
admin.empty_value_display = '**Empty**'


def api_urls():
    from importlib import import_module
    for app in settings.PROJECT_APP:
        try:
            import_module(app + '.urls')
        except Exception as e:
            logger_v1.error("import_module(app + '.urls')", extra={
                "detail": {
                    "error": e,
                }
            })
            continue


api_urls()

logger_v1.debug("APP START", extra={
    "detail": "from urls.py file , this is just for inform about app start"
})

urlpatterns = [

    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/auth/', obtain_jwt_token),
    url(r'^api/v1/token_refresh/', refresh_jwt_token),
    url(r'^api/v1/', include(api_v1_router.urls)),
    url(r'^api/v2/', include(api_v2_router.urls)),
    url(r'^api/v1/user/', include('apps.user.urls')),
    url(r'^api/v1/shop/', include('apps.shop.urls')),
    # url(r'^silk', include('silk.urls')),
    # url(r'^api/v1/announcements/', include('apps.announcements.urls')),
    # url(r'^api/v1/doc/auth/', include('rest_framework.urls', namespace='rest_framework')),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += patterns('', url(r'^silk', include('silk.urls', namespace='silk')))
# urlpatterns += url(r'^silk', include('silk.urls'))

"""
# Dynamic function decorator
# """
#
# SILKY_DYNAMIC_PROFILING = [{
#     'module': 'path.to.module',
#     'function': 'foo'
# }]
#
# # ... is roughly equivalent to
# @silk_profile()
# def foo():
#     pass
#
# """
# Dynamic method decorator
# """
#
# SILKY_DYNAMIC_PROFILING = [{
#     'module': 'path.to.module',
#     'function': 'MyClass.bar'
# }]
#
# # ... is roughly equivalent to
# class MyClass(object):
#
#     @silk_profile()
#     def bar(self):
#         pass
#
# """
# Dynamic code block profiling
# """
#
# SILKY_DYNAMIC_PROFILING = [{
#     'module': 'path.to.module',
#     'function': 'foo',
#     # Line numbers are relative to the function as opposed to the file in which it resides
#     'start_line': 1,
#     'end_line': 2,
#     'name': 'Slow Foo'
# }]
#
# # ... is roughly equivalent to
# def foo():
#     with silk_profile(name='Slow Foo'):
#         print (1)
#         print (2)
#     print(3)
#     print(4)