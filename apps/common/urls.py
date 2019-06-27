from dashboard.router import api_v1_router
from apps.common.viewsets import ApkReleaseViewSet, DisablePartViewSet

api_v1_router.register(prefix=r'apk_release', viewset=ApkReleaseViewSet, base_name='apk_release')


api_v1_router.register(prefix=r'disable_part', viewset=DisablePartViewSet, base_name='apk_release')

