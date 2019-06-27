from apps.announcements.viewset import AnnouncementViewSet, AnnouncementCountViewSet, MyAnnouncementViewSet
from dashboard.router import api_v1_router

api_v1_router.register(prefix=r'get_announcement_count', viewset=AnnouncementCountViewSet, base_name='get_announcement_count')
api_v1_router.register(prefix=r'announcements', viewset=AnnouncementViewSet, base_name='announcements_index')
api_v1_router.register(prefix=r'my_announcements', viewset=MyAnnouncementViewSet, base_name='my_announcements')
