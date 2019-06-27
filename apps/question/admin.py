import datetime

from random import randint
from django.conf.urls import url
from django.contrib import admin
from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django.core.exceptions import ObjectDoesNotExist

from apps.user.models import Advisor
from apps.question.models.managment import FaqQuestion
from apps.question.models.managment import AdvisorQuestion, QuestionBaseCategory
from apps.notification.tasks import send_notification_for_new_answer_to_student
from apps.question.models.questions import (
    Question,
    QuestionCategory,
    QuestionRejectHistory,
    QuestionFile,
    ConversionsComment
)


class QuestionFileInline(admin.StackedInline):
    model = QuestionFile
    extra = 0

    def get_exclude(self, request, obj=None):
        if obj and not request.user.is_superuser:
            self.exclude = ('file', 'title')
        return self.exclude

    def get_max_num(self, request, obj=None, **kwargs):
        if obj and not request.user.is_superuser:
            self.max_num = 0
        return self.max_num

    def get_readonly_fields(self, request, obj=None):
        if obj and not request.user.is_superuser:
            self.can_delete = False
            self.fields = [
                'file_link'
            ]
        return ['file_link']


class ConversionsCommentInline(admin.StackedInline):
    model = ConversionsComment
    readonly_fields = ['question', 'creator']
    extra = 0


class QuestionInline(admin.StackedInline):
    model = Question
    verbose_name = "Answer"
    verbose_name_plural = "Answers"
    extra = 0

    def get_max_num(self, request, obj=None, **kwargs):
        if obj and not request.user.is_superuser:
            self.max_num = 0
        return self.max_num

    def get_fields(self, request, obj=None):
        # if request.user.is_superuser:
        #     self.can_delete = True
        #     self.fields = [
        #         'body',
        #         'subject',
        #         'state',
        #         'status',
        #         'point',
        #         'main_category',
        #         'category',
        #         'view_count',
        #         'not_allow_user',
        #         'gender'
        #     ]
        #     return self.fields
        # else:
        self.can_delete = False
        self.fields = [
            'body',
        ]
        return self.fields


class QuestionAdmin(admin.ModelAdmin):
    prepopulated_fields = {}

    def get_readonly_fields(self, request, obj=None):
        return list(set(
            [field.name for field in self.opts.local_fields] +
            [field.name for field in self.opts.local_many_to_many]
        ))

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            self.inlines = [QuestionInline, QuestionFileInline, ConversionsCommentInline]
            self.fields = [
                'subject',
                'body',
                'state',
                'status',
                'point',
                'main_category',
                'category',
                'view_count',
                # 'creator',
                'not_allow_user',
                'gender'
            ]
            return self.fields
        else:
            self.fields = [
                'subject',
                'body',
                'main_category',
                'category',
            ]
            try:
                advisor = Advisor.objects.get(id=request.user.id)
                if advisor.state == 'expert' or advisor.state == "top_expert":
                    self.fields = [
                        'subject',
                        'body',
                    ]
                    self.inlines = [QuestionInline, QuestionFileInline, ConversionsCommentInline]

                elif advisor.state == "advisor":
                    self.inlines = []

            except Advisor.DoesNotExist:
                pass

        return self.fields

    def get_queryset(self, request):
        try:
            advisor = Advisor.objects.get(id=request.user.id)
            qs = super(QuestionAdmin, self).get_queryset(request)

            sub_categories = advisor.sub_categories.all()
            return qs.filter(
                type='question',
                category__in=sub_categories,
                state=advisor.state,
                gender=advisor.gender,
            ).filter(~Q(not_allow_user=request.user), ~Q(state="cartable"), ~Q(status="solved"))

        except ObjectDoesNotExist:
            qs = super(QuestionAdmin, self).get_queryset(request).filter()
            return qs.filter(type='question')

    def get_list_display(self, request):

        list_display = ('subject', 'status', 'create_datetime', 'category', 'main_category', 'gender')

        try:
            advisor = Advisor.objects.get(id=request.user.id)
            if advisor.state == 'advisor':
                list_display = ('subject', 'status', 'create_datetime', 'category')

            elif advisor.state == 'top_expert' or advisor.state == 'expert':
                list_display = ('subject', 'status', 'create_datetime', 'category', 'add_to_my_cartable_btn')

        except Advisor.DoesNotExist:
            pass

        return list_display

    @staticmethod
    def add_to_my_cartable_btn(obj):
        return format_html('<a href="{}">add_to_my_cartable</a>&nbsp;', reverse('admin:add_to_my_cartable', args=[obj.pk]))

    @transaction.atomic
    def add_to_my_cartable(self, request, question_id):

        user = Advisor.objects.get(id=request.user.id)
        question = Question.objects.get(id=question_id)

        try:
            count_of_sub_category = AdvisorQuestion.objects.filter(
                advisor=user,
                question__category=question.category
            ).count()

            if int(count_of_sub_category) >= 4:
                redirect_url = reverse(
                    'admin:question_question_changelist',
                    current_app=self.admin_site.name,
                )
                return HttpResponseRedirect(redirect_url)
        except ObjectDoesNotExist:
            pass

        try:
            AdvisorQuestion.objects.get(advisor=user, question=question)
        except ObjectDoesNotExist:
            advisor_question = AdvisorQuestion()
            advisor_question.status = 'waiting'
            advisor_question.advisor = user
            advisor_question.question = question
            advisor_question.save()

            question.state = 'cartable'
            question.save()

        redirect_url = reverse(
            'admin:question_question_changelist',
            current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(redirect_url)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^(?P<question_id>\d+)/add_to_my_cartable/$',
                self.admin_site.admin_view(self.add_to_my_cartable),
                name="add_to_my_cartable"
            )
        ]
        return custom_urls + urls

    def save_model(self, request, obj, form, change):
        try:
            advisor = Advisor.objects.get(id=request.user.id)
            if advisor.state == 'advisor':
                old_cat = self.get_object(request, obj.id).main_category.id
                if old_cat == obj.main_category.id:
                    obj.state = 'expert'

        except Advisor.DoesNotExist:
            pass

        obj.save()


#
# class AdvisorQuestionAdmin(admin.ModelAdmin):
#     list_display = ('question', 'created_at', 'status', 'reject_btn')
#
#     def get_queryset(self, request):
#         return super(AdvisorQuestionAdmin, self).get_queryset(request).filter(status='waiting', advisor_id=request.user.id)
#
#     @staticmethod
#     def reject_btn(obj):
#         return format_html('<a href="{}">reject it</a>&nbsp;', reverse('admin:reject', args=[obj.pk]))
#
#     @transaction.atomic
#     def reject_question(self, request, question_id):
#         advisor_question = AdvisorQuestion.objects.get(id=question_id)
#         question = advisor_question.question
#
#         create_reject_model = QuestionRejectHistory()
#         create_reject_model.reject_datetime = datetime.datetime.now()
#         create_reject_model.reject_by = request.user
#         create_reject_model.question = question
#         create_reject_model.gender = request.user.baseuser.gender
#         create_reject_model.save()
#
#         advisor_question = AdvisorQuestion.objects.get(question_id=question.id, advisor_id=request.user.id)
#         advisor_question.status = 'cant_answer'
#         advisor_question.save()
#
#         reject_count = QuestionRejectHistory.objects.filter(question=question).count()
#         if reject_count >= 3:
#             top_experts = Advisor.objects.filter(state='top_expert')
#             count_of_top_experts = top_experts.count()
#             if count_of_top_experts:
#                 random_number = randint(0, count_of_top_experts - 1)
#                 random_top_expert = top_experts[random_number]
#                 add_to_advisor_question = AdvisorQuestion()
#                 add_to_advisor_question.status = 'waiting'
#                 add_to_advisor_question.question = question
#                 add_to_advisor_question.advisor = random_top_expert
#                 add_to_advisor_question.save()
#                 question.state = 'top_expert'
#                 question.save()
#             else:
#                 question.state = 'expert'
#                 question.save()
#         else:
#             question.state = 'expert'
#             question.save()
#             question.not_allow_user.add(request.user)
#
#         redirect_url = reverse(
#             'admin:question_advisorquestion_changelist',
#             current_app=self.admin_site.name,
#         )
#         return HttpResponseRedirect(redirect_url)
#
#     @transaction.atomic
#     def answer_question(self, request):
#         question_id = request.POST.get("question_id")
#         advisor_question_id = request.POST.get("advisor_question_id")
#         query_set = AdvisorQuestion.objects.filter(
#             question_id=question_id,
#             advisor_id=request.user.id
#         ).select_related('question')
#
#         if query_set:
#             query_set = query_set.get()
#             answer = Question()
#             answer.body = request.POST['answer']
#             answer.creator = request.user
#             answer.answer_to = query_set.question
#             answer.state = 'advisor'
#             answer.type = 'answer'
#             answer.save()
#             query_set.question.status = "replied"
#             query_set.question.save()
#
#             send_notification_for_new_answer_to_student(query_set.question.id, query_set.question.creator_id)
#
#             for file in request.FILES.getlist('files[]', []):
#                 file_model = QuestionFile()
#                 file_model.file = file
#                 file_model.is_question = False
#                 file_model.question_id = answer.id
#                 file_model.gender = request.user.baseuser.gender
#                 file_model.uploader_id = request.user.id
#                 file_model.save()
#
#             request.method = "GET"
#             return self.change_view(request, advisor_question_id)
#         else:
#             return redirect('admin:index')
#
#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             url(
#                 r'^(?P<question_id>\d+)/reject/$',
#                 self.admin_site.admin_view(self.reject_question),
#                 name="reject"
#             ),
#             url(
#                 r'^answer_question/$',
#                 self.admin_site.admin_view(self.answer_question),
#                 name="answer_question"
#             ),
#             url(
#                 r'^delete_answer_question/$',
#                 self.admin_site.admin_view(self.delete_answer_question),
#                 name="delete_answer_question"
#             ),
#             url(
#                 r'^get_answer_question/$',
#                 self.admin_site.admin_view(self.get_answer_question),
#                 name="get_answer_question"
#             )
#         ]
#         return custom_urls + urls
#
#     def change_view(self, request, object_id, form_url='', extra_context=None):
#         advisor_question = AdvisorQuestion.objects.get(id=object_id)
#         question = Question.objects.get(id=advisor_question.question.id)
#         answers = Question.objects.filter(answer_to=advisor_question.question.id) \
#             .order_by('-create_datetime') \
#             .select_related('creator')
#
#         extra_context = extra_context or {}
#
#         extra_context['answers'] = answers
#         extra_context['question'] = question
#         extra_context['advisor_question_id'] = object_id
#
#         return super().change_view(
#             request, object_id, form_url, extra_context=extra_context,
#         )
#
#     @staticmethod
#     def delete_answer_question(request):
#         answer_id = request.POST.get('answer_id')
#         answer = Question.objects.filter(id=answer_id, creator_id=request.user.id)
#         if answer.exists():
#             answer.delete()
#             return JsonResponse({"message": "success"})
#         return JsonResponse({"message": "error"})
#
#     @staticmethod
#     def get_answer_question(request):
#         answer_id = request.POST.get('answer_id')
#         answer = Question.objects.filter(id=answer_id).select_related('creator')
#         if answer.exists():
#             answer = answer.get()
#             list_file = []
#             files = QuestionFile.objects.filter(question_id=answer.id)
#             for file in files:
#                 list_file.append(file.file_link())
#             answer = {
#                 "body": answer.body,
#                 "first_name": answer.creator.first_name,
#                 "last_name": answer.creator.last_name,
#                 "files": list_file,
#             }
#             return JsonResponse({"message": "success", "answer": answer})
#         return JsonResponse({"message": "not_found"})
#


class AdvisorQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at', 'advisor')


class FaqQuestionAdmin(admin.ModelAdmin):
    list_display = ('subject', 'create_datetime', 'create_by')
    exclude = ('create_by',)

    def get_queryset(self, request):
        try:
            user = Advisor.objects.get(id=request.user.id)
            return super(FaqQuestionAdmin, self).get_queryset(request).filter(create_by=user)
        except Advisor.DoesNotExist:
            return super(FaqQuestionAdmin, self).get_queryset(request).filter()

    def save_model(self, request, obj, form, change):
        try:
            user = Advisor.objects.get(id=request.user.id)
            obj.create_by = user
        except Advisor.DoesNotExist:
            pass
        obj.save()


class QuestionBaseCategoryAdmin(admin.ModelAdmin):
    pass


admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionCategory)
admin.site.register(FaqQuestion, FaqQuestionAdmin)
admin.site.register(QuestionBaseCategory, QuestionBaseCategoryAdmin)
# admin.site.register(AdvisorQuestion, AdvisorQuestionAdmin)
admin.site.register(AdvisorQuestion, AdvisorQuestionAdmin)
