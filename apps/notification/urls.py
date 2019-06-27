from dashboard.router import api_v1_router
from apps.notification.viewset import FcmTokenUserViewSet, NotificationViewSet, NotificationCountViewSet


api_v1_router.register(prefix=r'notify', viewset=NotificationViewSet, base_name='notify')
api_v1_router.register(prefix=r'get_notify_count', viewset=NotificationCountViewSet, base_name='get_notify_count')
api_v1_router.register(prefix=r'fcm_token_user', viewset=FcmTokenUserViewSet, base_name='fcm_token_user')
