from django.contrib.auth.models import User
from rest_framework import serializers

from utils.user_type import get_user_type
from apps.user.serializers import BaseSerializer
from apps.question.models.managment import (
    Advisor,
    AdvisorQuestion,
    FaqQuestion
)
from apps.question.models.questions import (
    ConversionsComment,
    QuestionFile,
    Question,
    QuestionBaseCategory,
    QuestionCategory,
)


class CreateQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class QuestionCreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')
        depth = 2


class QuestionUrlField(serializers.HyperlinkedModelSerializer):
    def to_representation(self, value):
        return '/' + value.url

    def to_internal_value(self, data):
        pass


class QuestionFilesSerializer(serializers.ModelSerializer):
    file = QuestionUrlField(read_only=True)

    class Meta:
        model = QuestionFile
        fields = (
            'id', 'file', 'title', 'size'
        )
        depth = 2


class QuestionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionCategory
        fields = '__all__'


class QuestionCategoryShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionCategory
        fields = ('id', 'title')


class QuestionBaseCategoryShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBaseCategory
        fields = ('id', 'title')


class QuestionBaseCategorySerializer(serializers.ModelSerializer):
    def get_user(self):
        r = self.context["request"]
        return r.user

    def _get_sub_categories(self, obj):
        user = self.get_user()
        subs = QuestionCategory.objects.filter(category=obj.id, gender__in=[user.baseuser.gender, None])
        subs = QuestionCategorySerializer(subs, read_only=True, many=True)
        return subs.data

    sub_categories = serializers.SerializerMethodField('_get_sub_categories')

    class Meta:
        model = QuestionBaseCategory
        fields = ('id', 'title', 'category_code', 'sub_categories')


class QuestionAnswersSerializer(serializers.ModelSerializer):
    files = QuestionFilesSerializer(read_only=True, many=True, source='get_files')

    @staticmethod
    def _user_type(obj):
        return get_user_type(obj.creator)

    user_type = serializers.SerializerMethodField('_user_type')

    class Meta:
        model = Question
        fields = (
            'id',
            'subject',
            'body',
            'point',
            'create_datetime',
            'user_type',
            'files'
        )
        depth = 1


class CreateQuestionSerializerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class ConversionsCommentSerializer(serializers.ModelSerializer):
    creator = QuestionCreatorSerializer(read_only=True)

    class Meta:
        model = ConversionsComment
        fields = '__all__'


class QuestionStudentSerializer(serializers.ModelSerializer):
    answers = QuestionAnswersSerializer(read_only=True, many=True, source='get_answers')
    files = QuestionFilesSerializer(read_only=True, many=True, source='get_files')
    main_category = QuestionBaseCategoryShowSerializer(many=False)
    category = QuestionCategoryShowSerializer(many=False)

    @staticmethod
    def _get_state(obj):
        return get_code_student_state(obj)

    code_state = serializers.SerializerMethodField('_get_state')

    @staticmethod
    def _user_type(obj):
        return get_user_type(obj.creator)

    user_type = serializers.SerializerMethodField('_user_type')

    class Meta:
        model = Question
        fields = (
            'id',
            'subject',
            'body',
            'create_datetime',
            'answers',
            'files',
            'category',
            'main_category',
            'user_type',
            'code_state',
        )
        depth = 1


class QuestionSerializerAdvisor(serializers.ModelSerializer):
    answers = QuestionAnswersSerializer(read_only=True, many=True, source='get_answers')
    files = QuestionFilesSerializer(read_only=True, many=True, source='get_files')
    main_category = QuestionBaseCategoryShowSerializer(many=False)
    category = QuestionCategoryShowSerializer(many=False)

    def _get_state(self, obj):
        return get_code_state(obj, self.context["request"].user)

    code_state = serializers.SerializerMethodField('_get_state')

    @staticmethod
    def _user_type(obj):
        return get_user_type(obj.creator)

    user_type = serializers.SerializerMethodField('_user_type')

    @staticmethod
    def get_comment_question(obj):
        comments = ConversionsComment.objects.filter(question_id=obj.id)

        if comments.exists():
            return ConversionsCommentSerializer(comments, many=True, read_only=True).data
        return []

    comments = serializers.SerializerMethodField('get_comment_question')

    class Meta:
        model = Question
        fields = (
            'id',
            'subject',
            'body',
            'create_datetime',
            'category',
            'user_type',
            'answers',
            'files',
            'main_category',
            'comments',
            'code_state',
            'creator_id',
            'has_in_faq'
        )
        depth = 1


class QuestionBoxStudentSerializer(serializers.ModelSerializer):
    def _get_state(self, obj):
        return get_code_student_state(obj)

    code_state = serializers.SerializerMethodField('_get_state')

    main_category = QuestionBaseCategoryShowSerializer(many=False)
    category = QuestionCategoryShowSerializer(many=False)

    class Meta:
        model = Question
        fields = (
            'id',
            'subject',
            'body',
            'create_datetime',
            'category',
            'main_category',
            'code_state',
        )
        depth = 1


class QuestionBoxSerializer(serializers.ModelSerializer):

    def _get_state(self, obj):
        return get_code_state(obj, self.context["request"].user)

    code_state = serializers.SerializerMethodField('_get_state')
    main_category = QuestionBaseCategoryShowSerializer(many=False)
    category = QuestionCategoryShowSerializer(many=False)

    class Meta:
        model = Question
        fields = (
            'id',
            'subject',
            'body',
            'create_datetime',
            'category',
            'main_category',
            'code_state',
        )
        depth = 1


# class QuestionRejectSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = QuestionRejectHistory
#         fields = '__all__'


class QuestionFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionFile
        fields = '__all__'


class AdvisorSerializer(serializers.ModelSerializer):
    user = QuestionCreatorSerializer(read_only=True)

    class Meta:
        model = Advisor
        fields = '__all__'
        depth = 2


class AdvisorQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvisorQuestion
        fields = '__all__'
        depth = 2


class FaqQuestionSerializer(serializers.ModelSerializer):
    create_by = BaseSerializer(many=False, read_only=True)

    class Meta:
        model = FaqQuestion
        fields = '__all__'
        depth = 2


class FaqQuestionManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaqQuestion
        fields = '__all__'
        depth = 1


class CreateFaqQuestionManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaqQuestion
        fields = '__all__'


def get_code_state(question, user):
    """
        status_choice = (
        (1, 'New'),
        (2, 'Accepted'),
        (3, 'Cartable'),
        (4, 'Replied'),
        (5, 'Solved'),
    )
    {% if question.code_state == "022" or question.code_state == "023" %}
            شما اجازه پاسخگویی ندارید
    {% elif question.code_state == "122" or question.code_state == "123" %}
            اضافه کردن به میز کار
            نمایش جزییات
    {% else %}
            درحال پاسخگویی
    {% endif %}

    """

    if question.status == 1 and question.state == "advisor":
        return "011"

    if question.status == 2 and question.state == "expert":
        if user in list(question.not_allow_user.all()):
            return "022"
        return "122"

    if question.status == 3 and question.state == "expert":
        return "132"

    if question.status == 4 and question.state == "expert":
        return "042"

    if question.status == 5 and question.state == "expert":
        return "052"

    if question.status == 2 and question.state == "top_expert":
        if user in list(question.not_allow_user.all()):
            return "023"
        return "123"

    if question.status == 3 and question.state == "top_expert":
        return "133"

    if question.status == 4 and question.state == "top_expert":
        return "043"

    if question.status == 5 and question.state == "top_expert":
        return "053"


def get_code_student_state(question):
    """
        {% if item.code_state == "11" %}
        <span class="text-danger">در انتظار بررسی</span>
        {% elif item.code_state == "32" %}
        <span class="text-danger">در حال پاسخگویی</span>
        {% elif item.code_state == "52" %}
        <span class="text-success">به جواب رسیدم</span>
        {% elif item.code_state == "42" %}
        <span class="text-success">پاسخ جدید</span>
        {% elif item.code_state == "23" %}
        <span class="text-danger">در حال بررسی بیشتر</span>
        {% elif item.code_state == "33" %}
        <span class="text-danger">در حال پاسخگویی توسط مشاور ارشد</span>
        {% endif %}

    """

    if (question.status == 1 and question.state == "advisor") or (question.status == 2 and question.state == "expert"):
        return "11"

    if question.status == 3 and question.state == "expert":
        return "32"

    if (question.status == 4 and question.state == "expert") or (question.status == 4 and question.state == "top_expert"):
        return "42"

    if (question.status == 5 and question.state == "expert") or (question.status == 5 and question.state == "top_expert"):
        return "52"

    if question.status == 2 and question.state == "top_expert":
        return "23"

    if question.status == 3 and question.state == "top_expert":
        return "33"
