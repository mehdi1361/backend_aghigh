from dashboard.router import api_v1_router
from dashboard.router import api_v2_router
from apps.activity.viewsets import (
    AdditionalFieldViewSet,
    ActivityViewSet,
    GroupAdditionalFieldViewSet,
    ActivityCategoryViewSet,
    CategoriesReportViewSet,
    ActivityApiSadafViewSet,
    ActivityReadOnlyViewSet,
    ActivityCategorySadafViewSet,
    SchoolSadafViewSet,
    ReportAbusesViewSet
)

api_v1_router.register(prefix=r'activities', viewset=ActivityViewSet, base_name='activities')
api_v1_router.register(prefix=r'activity_categories', viewset=ActivityCategoryViewSet, base_name='activity_categories')
api_v1_router.register(prefix=r'additional_fields', viewset=AdditionalFieldViewSet, base_name='additional_fields')
api_v1_router.register(
    prefix=r'groups_additional_fields',
    viewset=GroupAdditionalFieldViewSet,
    base_name='groups_additional_fields'
)
api_v1_router.register(prefix=r'categories_reports', viewset=CategoriesReportViewSet, base_name='categories_reports')
api_v1_router.register(prefix=r'report_abuses', viewset=ReportAbusesViewSet, base_name='report_abuses')

api_v1_router.register(prefix=r'activity_sadaf', viewset=ActivityApiSadafViewSet, base_name='activity_sadaf')
api_v1_router.register(prefix=r'category_sadaf', viewset=ActivityCategorySadafViewSet, base_name='category_sadaf')
api_v1_router.register(prefix=r'school_sadaf', viewset=SchoolSadafViewSet, base_name='school_sadaf')


api_v2_router.register(prefix=r'activities', viewset=ActivityReadOnlyViewSet, base_name='activities_v2')
api_v2_router.register(prefix=r'activity_categories', viewset=ActivityCategoryViewSet, base_name='activity_categories')
