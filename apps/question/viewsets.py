import copy
import threading
import datetime

from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from utils.user_type import get_user_level
from apps.common.viewsets import BaseViewSet, LargeResultsSetPagination
from apps.notification.tasks import send_notification_for_new_answer_to_student, send_notification_for_new_answer_to_teacher
from apps.question.models.managment import (
    FaqQuestion,
    AdvisorQuestion
)
from apps.question.models.questions import (
    QuestionFile,
    QuestionRejectHistory,
    QuestionBaseCategory,
    QuestionCategory,
    ConversionsComment,
    Question,
)
from apps.question.serializer import (
    QuestionCategorySerializer,
    QuestionSerializerAdvisor,
    CreateQuestionSerializer,
    QuestionBaseCategorySerializer,
    FaqQuestionSerializer,
    ConversionsCommentSerializer,
    QuestionBoxSerializer,
    CreateQuestionSerializerSerializer,
    QuestionBoxStudentSerializer,
    QuestionStudentSerializer,
    FaqQuestionManagerSerializer,
    CreateFaqQuestionManagerSerializer,
)


class QuestionViewSet(BaseViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionBoxStudentSerializer

    @staticmethod
    def get_params(request):
        query_params = request.query_params.copy()
        dict_params = {}
        list_param_int = ['category', 'sub_category', 'order']
        for key, value in query_params.items():
            if key in list_param_int:
                if query_params[key].isdigit():
                    dict_params[key] = int(value)
                    continue
        return dict_params

    @staticmethod
    def get_query(dict_params):
        query = {}
        order = {}

        if 'category' in dict_params:
            query['category__category_id'] = dict_params['category']

        if 'sub_category' in dict_params:
            query['category_id'] = dict_params['sub_category']

        if 'order' in dict_params and dict_params['order']:
            order = '-create_datetime'

        return query, order

    def list(self, request, *args, **kwargs):

        params = self.get_params(request)
        query, order = self.get_query(params)
        query["creator_id"] = request.user.id
        query["type"] = "question"
        queryset = self.queryset.filter(**query).order_by(order if order else '-create_datetime')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def save_file(self, files, question):
        for file in files:
            file_model = QuestionFile()
            file_model.file = file
            file_model.question = question
            file_model.gender = self.request.user.baseuser.gender
            file_model.uploader_id = self.request.user.id
            file_model.save()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        self.serializer_class = CreateQuestionSerializerSerializer
        try:
            data = copy.copy(request.data)

            data["type"] = "question"
            data["answer_to"] = None

            if "conversation_id" in data:
                data["answer_to"] = data["conversation_id"]
                data["subject"] = "answer"
                data["type"] = "answer"

                question = Question.objects.get(id=data["conversation_id"])
                question.status = 3
                question.save()

                try:
                    advisor_question = AdvisorQuestion.objects.get(question=question)
                    send_notification = threading.Thread(target=send_notification_for_new_answer_to_teacher, args=(question.id, advisor_question.advisor.id))
                    send_notification.start()

                except:
                    pass

            else:
                data["main_category"] = int(data.get('category'))

                if data.get('sub_category'):
                    data["category"] = int(data.get('sub_category'))
                    data.pop('sub_category')

            data["creator"] = request.user.id
            data["gender"] = request.user.baseuser.gender

            self.serializer_class = CreateQuestionSerializer
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:

            return Response({"message": e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        question = serializer.save()
        data = self.request.data
        self.save_file(data.getlist('files[]', []), question)

    @transaction.atomic
    def change_question_status(self, request, question_id, new_status):

        queryset = self.queryset.filter(pk=question_id, creator_id=request.user.id).select_related('answer_to')

        if not queryset.exists():
            return status.HTTP_400_BAD_REQUEST, "question not exits"

        question = queryset.get()

        if new_status == "solved":
            question.status = 5

        if new_status == "not_solved":
            question.state = "top_expert"
            question.status = 2
            advisor_question = AdvisorQuestion.objects.get(question=question)
            question.not_allow_user.add(advisor_question.advisor.id)
            advisor_question.delete()

        elif new_status == "disinterested":
            question.status = 2
            advisor_question = AdvisorQuestion.objects.get(question=question)
            question.not_allow_user.add(advisor_question.advisor.id)
            advisor_question.delete()

        question.save()

        return status.HTTP_200_OK, ""

    @list_route(url_path='score', methods=['post'])
    def set_question_score(self, request):
        try:
            question = self.queryset.get(id=request.data.get('question_id'), type='answer')
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'answer not exits'})

        question.point = request.data.get('point')
        question.save()

        return Response(status=status.HTTP_200_OK, data={'message': ''})

    @detail_route(url_path='solved', methods=['post'])
    def set_question_solved(self, request, pk=None):

        _status, message = self.change_question_status(request=request, question_id=pk, new_status="solved")
        return Response(status=_status, data={'message': message})

    @detail_route(url_path='not_solved', methods=['post'])
    def set_question_note_solved(self, request, pk=None):

        _status, message = self.change_question_status(request=request, question_id=pk, new_status="not_solved")
        return Response(status=_status, data={'message': message})

    @detail_route(url_path='disinterested', methods=['post'])
    def set_question_note_disinterested(self, request, pk=None):

        _status, message = self.change_question_status(request=request, question_id=pk, new_status="disinterested")

        return Response(status=_status, data={'message': message})

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = QuestionStudentSerializer
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class FaqQuestionViewSet(BaseViewSet):
    queryset = FaqQuestion.objects.all()
    serializer_class = FaqQuestionSerializer

    @staticmethod
    def get_params(request):
        query_params = request.query_params.copy()
        dict_params = {}
        list_param_int = ['point_start', 'point_end', 'category', 'sub_category', 'order']
        for key, value in query_params.items():
            if key in list_param_int:
                if query_params[key].isdigit():
                    dict_params[key] = int(value)
                    continue
        return dict_params

    @staticmethod
    def get_query(dict_params, request):
        query = {}
        order = {}

        query['gender'] = request.user.baseuser.gender

        if 'category' in dict_params:
            query['category_id'] = dict_params['category']

        if 'point_start' in dict_params:
            query['point__gte'] = dict_params['point_start']

        if 'point_end' in dict_params:
            query['point__lte'] = dict_params['point_end']

        if 'sub_category' in dict_params:
            query['sub_category_id'] = dict_params['sub_category']

        if 'order' in dict_params and dict_params['order']:
            order = '-create_datetime'

        return query, order

    def list(self, request, *args, **kwargs):
        params = self.get_params(request)
        query, order = self.get_query(params, request)
        queryset = self.queryset.filter(**query).order_by(order if order else 'create_datetime')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        pass


class FaqQuestionManagerViewSet(BaseViewSet):
    queryset = FaqQuestion.objects.all()
    serializer_class = FaqQuestionManagerSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        self.serializer_class = CreateFaqQuestionManagerSerializer

        data = copy.copy(request.data)
        data["create_by_id"] = request.user.id

        if data["action"] == "page_question":
            question = Question.objects.filter(id=data["question_id"], has_in_faq=False)
            if not question.exists():
                return Response("question not exits", status=status.HTTP_400_BAD_REQUEST)

            question = question.get()
            data["category"] = question.main_category_id
            data["sub_category"] = question.category_id
            data["gender"] = question.gender
            data["related_question_id"] = question.pk
            question.has_in_faq = True
            question.save()
        else:
            user_level = get_user_level(request.user, 'advisor')[0]
            try:
                sub_category = QuestionCategory.objects.get(id=data["sub_category"])
            except:
                return Response("question not exits", status=status.HTTP_404_NOT_FOUND)

            if user_level != "top_expert" and sub_category not in request.user.baseuser.advisor.sub_categories.all():
                return Response("you don't have permission", status=status.HTTP_403_FORBIDDEN)

            data["gender"] = sub_category.gender
            data["category"] = sub_category.category_id
            data["is_accepted"] = True

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    @list_route(url_path='accept', methods=['post'])
    def accept_faq_question(self, request):
        data = request.data
        try:
            faq_question = self.queryset.get(pk=data.get("question_id"))
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        faq_question.is_accepted = True
        faq_question.save()
        return Response(status=status.HTTP_200_OK)

    @transaction.atomic
    @list_route(url_path='remove', methods=['post'])
    def remove_faq_question(self, request):
        data = request.data
        try:
            faq_question = self.queryset.get(pk=data.get("question_id"))
            question = Question.objects.get(pk=faq_question.related_question_id)
        except:
            return Response(status=status.HTTP_4question04_NOT_FOUND)

        question.has_in_faq = False
        question.save()

        faq_question.delete()
        return Response(status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save()

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(
            sub_category__in=request.user.baseuser.advisor.sub_categories.all(),
            is_accepted=False
        ).order_by('create_datetime')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class QuestionManagerViewSet(BaseViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionBoxSerializer

    def list(self, request, *args, **kwargs):
        _level = request.query_params.get('role')

        q_object = Q()
        q_object.add(Q(type='question'), Q.AND)
        q_object.add(Q(state=_level), Q.AND)
        q_object.add(Q(gender=request.user.baseuser.gender), Q.AND)
        q_object.add(~Q(status=5), Q.AND)

        if _level == "advisor":
            q_object.add(Q(main_category=request.user.baseuser.advisor.category), Q.AND)

        else:
            q_object.add(Q(category__in=request.user.baseuser.advisor.sub_categories.all()), Q.AND)

        queryset = self.queryset.filter(q_object)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = QuestionSerializerAdvisor
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @transaction.atomic
    @list_route(url_path='confirm', methods=['post'])
    def confirm_question(self, request):
        data = request.data

        queryset = self.queryset.filter(id=data["question_id"], main_category=request.user.baseuser.advisor.category)
        if queryset.exists():
            question = queryset.get()
            main_cat = question.main_category
            new_main_cat = data['category']

            question.category = None
            if int(new_main_cat) == main_cat.id:
                question.state = "expert"
                question.status = 2
                new_sub_cat = data.get('sub_category', 0)

                new_cat = QuestionCategory.objects.filter(id=new_sub_cat)
                if not new_cat.exists() or new_cat.get().category_id != int(new_main_cat):
                    return Response(status=status.HTTP_404_NOT_FOUND)

                question.category_id = new_sub_cat

            question.main_category_id = new_main_cat

            question.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @transaction.atomic
    @list_route(url_path='answer', methods=['post'])
    def answer_question(self, request):
        question_id = request.data.get("question_id")
        query_set = AdvisorQuestion.objects.filter(
            question_id=question_id,
            advisor_id=request.user.id
        )

        if query_set.exists():
            query_set = query_set.get()

            answer = self.create_answer(query_set, request)
            query_set.question.status = 4
            query_set.question.save()

            try:
                send_notification = threading.Thread(target=send_notification_for_new_answer_to_student, args=(query_set.question.id, query_set.question.creator_id))
                send_notification.start()
            except:
                pass

            self.save_files(answer, request)

            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def save_files(answer, request):
        for file in request.data.getlist('files[]', []):
            file_model = QuestionFile()
            file_model.file = file
            file_model.is_question = False
            file_model.question_id = answer.id
            file_model.gender = request.user.baseuser.gender
            file_model.uploader_id = request.user.id
            file_model.save()

    @staticmethod
    def create_answer(query_set, request):
        answer = Question()
        answer.body = request.data["body"]
        answer.creator = request.user
        answer.answer_to = query_set.question
        answer.state = 'advisor'
        answer.type = 'answer'
        answer.save()
        return answer

    @list_route(url_path='workspace', methods=['get'])
    def get_workspace(self, request):
        role = request.GET.get('role', False)
        roles = get_user_level(request.user, 'advisor')
        if role not in roles:
            raise ValidationError({"message": "user no has permission"}, code=status.HTTP_400_BAD_REQUEST)

        queryset = self.queryset.filter(
            advisor_question__advisor_id=request.user.id,
            state=role,
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @transaction.atomic
    @list_route(url_path='pick_question', methods=['post'])
    def pick_question(self, request):
        data = request.data

        question = Question.objects.filter(id=data["question_id"])
        if question.exists():
            question = question.get()
            queryset = AdvisorQuestion.objects.filter(
                advisor=request.user,
                question__category=question.category
            )

            # کد زیر برای پویا کردن فعال کردن و غیر فعال کردن محدودیت تعداد سوالات باز کارتابل مشاوران درج شده
            from .config import Restriction_Open_Questions, Count_Open_Questions
            if Restriction_Open_Questions:
                if queryset.count() >= Count_Open_Questions:
                    return Response({"message": "you have high than" + str(Count_Open_Questions) + "question in cartable"}, status.HTTP_403_FORBIDDEN)

            # محدودیت تعداد سوالات بازی که هر مشاور می تواند در کارتابل داشته باشد
            #  بنا به درخواست مجدد اتحادیه- آقای خداجو- حذف شد
            # if queryset.count() >= 4:
            #     return Response({"message": "you have high than 4 question in cartable"}, status.HTTP_403_FORBIDDEN)

            if question.category not in list(request.user.baseuser.advisor.sub_categories.all()):
                return Response(status=status.HTTP_403_FORBIDDEN)

            if queryset.filter(question=question).exists():
                return Response(status=status.HTTP_200_OK)

            advisor_question = AdvisorQuestion()
            advisor_question.status = 'waiting'
            advisor_question.advisor = request.user.baseuser.advisor
            advisor_question.question = question
            advisor_question.save()

            question.status = 3
            question.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @transaction.atomic
    @list_route(url_path='reject', methods=['post'])
    def reject_question(self, request):
        data = request.data
        try:
            advisor_question = AdvisorQuestion.objects.get(question=data.get("question_id"), advisor=request.user.baseuser.advisor)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        question = advisor_question.question

        reject_question = QuestionRejectHistory.objects.filter(question=question)
        if not reject_question.filter(reject_by=request.user).exists():
            self.add_to_reject_history(question, request)
            question.not_allow_user.add(advisor_question.advisor.id)

        question.status = 2
        question.state = 'expert'

        reject_count = reject_question.count()
        if reject_count >= 3:
            question.state = 'top_expert'

        question.save()
        advisor_question.delete()
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def add_to_reject_history(question, request):
        create_reject_model = QuestionRejectHistory()
        create_reject_model.reject_datetime = datetime.datetime.now()
        create_reject_model.reject_by = request.user
        create_reject_model.question = question
        create_reject_model.gender = request.user.baseuser.gender
        create_reject_model.save()

    @transaction.atomic
    @list_route(url_path='records', methods=['get'])
    def records_question(self, request):
        try:
            question = self.queryset.get(id=request.query_params['question_id'])
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        queryset = self.queryset.filter(
            category_id=question.category_id,
            main_category_id=question.main_category_id,
            creator=question.creator,
        ).order_by('-create_datetime').exclude(id=question.id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(url_path='statistics', methods=['get'])
    def statistics(self, request):
        self.queryset = self.queryset.filter(category__in=request.user.baseuser.advisor.sub_categories.all()).all()

        queryset = {
            "all": self.queryset.filter().count(),
            "male": self.queryset.filter(gender='male').count(),
            "female": self.queryset.filter(gender='female').count(),

            "advisor_pending": self.queryset.filter(state='advisor', status=1).count(),

            "student_pending": self.queryset.filter(status=4).count(),

            "expert_cartable": self.queryset.filter(state='expert', status=2).count(),
            "expert_pending": self.queryset.filter(state='expert', status=3).count(),
            "expert_solved": self.queryset.filter(state='expert', status=5).count(),

            "top_expert_cartable": self.queryset.filter(state='top_expert', status=2).count(),
            "top_expert_pending": self.queryset.filter(state='top_expert', status=3).count(),
            "top_expert_solved": self.queryset.filter(state='top_expert', status=5).count(),
        }
        return Response(queryset)


class QuestionCommentManagerViewSet(BaseViewSet):
    queryset = ConversionsComment.objects.all()
    serializer_class = ConversionsCommentSerializer

    def list(self, request, *args, **kwargs):
        data = request.query_params

        queryset = self.queryset.filter(question_id=data["question_id"]).order_by('-create_datetime')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = copy.copy(request.data)
        data["creator_id"] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class QuestionCategoryViewSet(BaseViewSet):
    queryset = QuestionBaseCategory.objects.all()
    serializer_class = QuestionBaseCategorySerializer
    pagination_class = LargeResultsSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(url_path='sub_categories', methods=['get'])
    def sub_categories(self, request, pk=None):

        self.queryset = QuestionCategory.objects.all()
        self.serializer_class = QuestionCategorySerializer
        queryset = self.queryset.filter(category_id=pk, gender=request.user.baseuser.gender)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class QuestionBaseCategoryViewSet(BaseViewSet):
    queryset = QuestionBaseCategory.objects.all()
    serializer_class = QuestionBaseCategorySerializer
