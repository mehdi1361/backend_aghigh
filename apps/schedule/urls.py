from dashboard.router import api_v1_router
from apps.schedule.viewsets import (
    AnnualEventsViewSet,
    OccurrenceViewSet,
    EventViewSet,
)


api_v1_router.register(r'event', EventViewSet)
api_v1_router.register(r'annual_events', AnnualEventsViewSet)
api_v1_router.register(r'occurrence', OccurrenceViewSet)
