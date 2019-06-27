from dashboard.router import api_v1_router
from apps.question.viewsets import (
    QuestionViewSet,
    QuestionCategoryViewSet,
    FaqQuestionViewSet,
    QuestionManagerViewSet,
    FaqQuestionManagerViewSet,
    QuestionCommentManagerViewSet,
    QuestionBaseCategoryViewSet,
    # QuestionRejectViewSet,
)

api_v1_router.register(prefix=r'questions', viewset=QuestionViewSet, base_name='questions_index')
api_v1_router.register(prefix=r'questions_category', viewset=QuestionCategoryViewSet, base_name='question_category_index')
api_v1_router.register(prefix=r'questions_base_category', viewset=QuestionBaseCategoryViewSet, base_name='question_base_category_index')
api_v1_router.register(prefix=r'faq_questions', viewset=FaqQuestionViewSet, base_name='faq_questions_index')

api_v1_router.register(prefix=r'faq_manager', viewset=FaqQuestionManagerViewSet, base_name='faq_manager')
api_v1_router.register(prefix=r'questions_manager', viewset=QuestionManagerViewSet, base_name='questions_manager')
api_v1_router.register(prefix=r'questions_comment', viewset=QuestionCommentManagerViewSet, base_name='questions_comment')

# api_v1_router.register(prefix=r'questions_reject_history', viewset=QuestionRejectViewSet, base_name='question_reject_history_index')
