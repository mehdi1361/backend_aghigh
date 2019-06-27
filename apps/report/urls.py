from dashboard.router import api_v1_router
from apps.report.viewsets import (
    ActivityReportViewSet,
    UserReportViewSet,
    SchoolReportViewSet,
    ReportsViewSet
)

api_v1_router.register(prefix=r'activity_reports', viewset=ActivityReportViewSet, base_name='activity_reports')
api_v1_router.register(prefix=r'user_reports', viewset=UserReportViewSet, base_name='user_reports')
api_v1_router.register(prefix=r'school_reports', viewset=SchoolReportViewSet, base_name='school_reports')
api_v1_router.register(prefix=r'reports', viewset=ReportsViewSet, base_name='reports')
