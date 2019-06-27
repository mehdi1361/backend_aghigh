from dashboard.router import api_v1_router
from apps.emtiaz.viewset import ParamViewSet, ActivityCommentViewSet, EmtiazViewSet


api_v1_router.register(prefix=r'emtiaz', viewset=EmtiazViewSet, base_name='emtiaz')
api_v1_router.register(prefix=r'params', viewset=ParamViewSet, base_name='params')
api_v1_router.register(prefix=r'activity_comment', viewset=ActivityCommentViewSet, base_name='activity_comment')
