from apps.league.viewset import LeagueViewSet, ProvinceViewSet, TeacherSchool, CountyViewSet, CampViewSet
from dashboard.router import api_v1_router


api_v1_router.register(prefix=r'league', viewset=LeagueViewSet, base_name='league')
api_v1_router.register(prefix=r'League', viewset=LeagueViewSet, base_name='League')
api_v1_router.register(prefix=r'provinces', viewset=ProvinceViewSet, base_name='provinces')
api_v1_router.register(prefix=r'counties', viewset=CountyViewSet, base_name='counties')
api_v1_router.register(prefix=r'camps', viewset=CampViewSet, base_name='camps')
api_v1_router.register(prefix=r'teacher_schools', viewset=TeacherSchool, base_name='teacher_schools')
