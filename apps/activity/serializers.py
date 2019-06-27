import datetime
import json

from django.db.models import Sum
from rest_framework import serializers

from apps.activity.messages import START_DATE_LESS_THAN_END_DATE
from apps.activity.static import REVIEW_STATE
from apps.emtiaz.models import ActivityComment
from apps.user.serializers import StudentSerializer, SchoolSerializer, TeacherSerializer, SchoolSerializerSadaf
from apps.activity.models import (
    AdditionalField,
    ActivityCategory,
    Activity,
    ImageActivity,
    FileActivity,
    ActivityLike,
    GroupAdditionalFields,
    ActivityAdditionalFields,
    DropDownFormSomeAdditionalField,
    RateActivity,
    CategoriesReport,
    ReportAbuse)


class DropDownSerializer(serializers.ModelSerializer):

    @staticmethod
    def _get_group_select_id(obj):
        return obj['group_select_id']

    group_select_id = serializers.SerializerMethodField("_get_group_select_id")

    class Meta:
        model = DropDownFormSomeAdditionalField
        fields = ('id', 'value', 'group_select_id')
        # fields = ('id', 'value','sub_form_id')
        # fk_name = "additional_field"
        # fields = '__all__'


class GroupAdditionalFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupAdditionalFields
        fields = '__all__'


class AdditionalFieldSerializer(serializers.ModelSerializer):
    values = DropDownSerializer(many=True, read_only=True, source='get_drop_down', )

    class Meta:
        model = AdditionalField
        fields = (
            'id',
            'label',
            'field_type',
            'category',
            'required',
            'values',
            'group',
            'order',
            'validate_data'
        )


class ActivityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityCategory
        fields = ('id', 'title', 'slug')


class UrlField(serializers.HyperlinkedModelSerializer):
    def to_representation(self, value):
        return '/' + value.url

    def to_internal_value(self, data):
        pass


class ImageSerializer(serializers.ModelSerializer):
    image = UrlField(read_only=True)

    class Meta:
        model = ImageActivity
        fields = ('id', 'title', 'comment', 'status', 'image', 'size')


class FilesSerializer(serializers.ModelSerializer):
    file = UrlField(read_only=True)

    class Meta:
        model = FileActivity
        fields = ('id', 'title', 'comment', 'status', 'file', 'size')


class ActivityAdditionalFieldSerializer(serializers.ModelSerializer):
    @staticmethod
    def _get_drop_down_text(obj):

        if obj.additional_field.field_type == "drop_down":
            try:
                return DropDownFormSomeAdditionalField.objects.filter(
                    id=int(obj.value),
                    additional_field=obj.additional_field
                ).get().value
            except:
                return obj.value

        elif obj.additional_field.field_type == "check_box":
            return obj.additional_field.label

        # elif obj.additional_field.field_type == "file_upload":
        #     return json.loads(obj.value)
        else:
            return obj.value

    @staticmethod
    def _get_type_additional_filed(obj):
        return obj.additional_field.field_type

    @staticmethod
    def _get_files_value(obj):
        if obj.additional_field.field_type == "file_upload":
            return json.loads(obj.value)
        else:
            return {}

    files_value = serializers.SerializerMethodField('_get_files_value')
    text_value = serializers.SerializerMethodField('_get_drop_down_text')
    field_type = serializers.SerializerMethodField('_get_type_additional_filed')

    class Meta:
        model = ActivityAdditionalFields
        fields = (
            'id',
            'additional_field',
            'text_value',
            'field_type',
            'value',
            'status',
            'comment',
            'files_value'
        )


class ActivitySerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True, source='get_images')
    files = FilesSerializer(many=True, read_only=True, source='get_files')
    additional_field = ActivityAdditionalFieldSerializer(many=True, read_only=True, source='get_additional_field')
    student = StudentSerializer(many=False, read_only=True)
    category = ActivityCategorySerializer(many=False, read_only=True)
    school = SchoolSerializer(many=False, read_only=True)

    def get_user(self):
        r = self.context["request"]
        return r.user

    @staticmethod
    def get_likes_count(obj):

        likes = ActivityLike.objects.using(obj._state.db).filter(activity_id=obj.id)
        return likes.count()

    def _get_liked_by_user(self, obj):

        likes = ActivityLike.objects.using(obj._state.db).filter(activity_id=obj.id, liker=self.get_user())
        if likes.exists():
            return True
        return False

    def _get_user_rate(self, obj):
        _dict_rate = {
            "count": obj.rate_count,
            'average': float("{0:.2f}".format(obj.point_emtiaz))
        }
        rate = RateActivity.objects.using(obj._state.db).filter(activity_id=obj.id, student=self.get_user())

        if rate.exists():
            rate = rate.get()
            _dict_rate["user_rate"] = rate.rate
        else:
            _dict_rate["user_rate"] = 0

        return _dict_rate

    def _get_user_has_comment(self, obj):

        comment = ActivityComment.objects.using(obj._state.db).filter(activity_id=obj.id, sender=self.get_user())
        if comment.exists():
            return True
        return False

    @staticmethod
    def _get_point(obj):
        activity_point = RateActivity.objects.using(obj._state.db).filter(
            activity_id=obj.id,
            rate__gt=3
        ).aggregate(Sum('average_absolute'))["average_absolute__sum"]
        if activity_point is not None:
            return activity_point
        return 0

    @staticmethod
    def _get_point_star(obj):
        return {
            "sum": obj.point_emtiaz_sum,
            "count": obj.rate_count
        }

    like_count = serializers.SerializerMethodField('get_likes_count')
    liked_by_user = serializers.SerializerMethodField('_get_liked_by_user')
    user_has_comment = serializers.SerializerMethodField('_get_user_has_comment')
    rate = serializers.SerializerMethodField('_get_user_rate')
    point_star = serializers.SerializerMethodField('_get_point_star')

    class Meta:
        model = Activity
        fields = (
            'id',
            'school',
            'images',
            'files',
            'additional_field',
            'student',
            'liked_by_user',
            'like_count',
            'user_has_comment',
            'point_star',
            'rate',
            'checker',
            'category',
            'category_status',
            'category_comment',
            'title',
            'title_comment',
            'title_status',
            'location',
            'location_comment',
            'location_status',
            'start_date',
            'start_date_comment',
            'start_date_status',
            'end_date',
            'end_date_comment',
            'end_date_status',
            'description',
            'description_comment',
            'description_status',
            'state',
            'created_at',
            'updated_at',
            'accepted_at',
            'vip',
            'view_count',
            'like_count',
            'point_emtiaz',
            'point_emtiaz_sum',
            'point',
            'rate_count',
            'gender',
            "get_school_name",
            'get_province_name',
            'get_county_name',
            'general_comment'
        )

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError(START_DATE_LESS_THAN_END_DATE, code=400)
        return data


class BoxActivitySerializer(serializers.ModelSerializer):
    @staticmethod
    def get_likes_count(obj):
        likes = ActivityLike.objects.using(obj._state.db).filter(activity_id=obj.id)
        return likes.count()

    @staticmethod
    def _get_point_star(obj):
        return {
            "sum": obj.point_emtiaz_sum,
            "count": obj.rate_count
        }

    @staticmethod
    def _get_image(obj):
        images = ImageActivity.objects.using(obj._state.db).filter(activity_id=obj.id, archive=False)
        image = ""
        if images:
            image = '/' + images[0].image.url
        return image

    @staticmethod
    def _get_activity_year(obj):
        return obj._state.db

    activity_year = serializers.SerializerMethodField('_get_activity_year')
    image = serializers.SerializerMethodField('_get_image')
    like_count = serializers.SerializerMethodField('get_likes_count')
    point_star = serializers.SerializerMethodField('_get_point_star')
    student = StudentSerializer(many=False, read_only=True)
    school = SchoolSerializer(many=False, read_only=True)

    class Meta:
        model = Activity
        fields = (
            'id',
            'title',
            'location',
            'image',
            'like_count',
            'view_count',
            'point',
            'student',
            'school',
            'state',
            'point_emtiaz',
            'created_at',
            'updated_at',
            'activity_year',
            'point_star',
            'general_comment'
        )


class BoxActivityHistoryCoachSerializer(BoxActivitySerializer):
    school = SchoolSerializer(many=False, read_only=True)

    @staticmethod
    def _get_review_state(obj):
        return ""

    review_state = serializers.SerializerMethodField('_get_review_state')

    class Meta:
        model = Activity
        fields = (
            'id',
            'title',
            'location',
            'image',
            'like_count',
            'view_count',
            'point',
            'school',
            'student',
            'state',
            'point_emtiaz',
            'created_at',
            'updated_at',
            'review_state'
        )


class BoxActivityWorkspaceCoachSerializer(BoxActivitySerializer):
    school = SchoolSerializer(many=False, read_only=True)

    @staticmethod
    def _get_review_state(obj):
        time_threshold = (datetime.datetime.now() - obj.updated_at).days

        if time_threshold <= 1:
            return REVIEW_STATE["GREEN"]

        elif 1 < time_threshold == 2:
            return REVIEW_STATE["YELLOW"]

        elif 2 < time_threshold == 3:
            return REVIEW_STATE["RED"]

        elif time_threshold > 3:
            return REVIEW_STATE["DARK"]

    review_state = serializers.SerializerMethodField('_get_review_state')

    class Meta:
        model = Activity
        fields = (
            'id',
            'title',
            'location',
            'image',
            'like_count',
            'view_count',
            'point',
            'school',
            'student',
            'state',
            'point_emtiaz',
            'created_at',
            'updated_at',
            'review_state'
        )


class BoxActivityWorkspaceOtherLevelSerializer(BoxActivitySerializer):
    school = SchoolSerializer(many=False, read_only=True)

    @staticmethod
    def _get_review_state(obj):
        time_threshold = (datetime.datetime.now() - obj.updated_at).days

        if time_threshold <= 4:
            return REVIEW_STATE["GREEN"]

        elif 4 < time_threshold == 5:
            return REVIEW_STATE["YELLOW"]

        elif 5 < time_threshold == 6:
            return REVIEW_STATE["RED"]

        elif time_threshold > 6:
            return REVIEW_STATE["DARK"]

    review_state = serializers.SerializerMethodField('_get_review_state')

    class Meta:
        model = Activity
        fields = (
            'id',
            'title',
            'location',
            'image',
            'like_count',
            'view_count',
            'point',
            'school',
            'student',
            'state',
            'point_emtiaz',
            'created_at',
            'updated_at',
            'review_state'
        )


class CreateActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'

    def validate(self, data):
        now = datetime.datetime.now()
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError({"start_date_lower": START_DATE_LESS_THAN_END_DATE}, code=400)

        if data['start_date'] > now or data['end_date'] > now:
            raise serializers.ValidationError({"date_future": START_DATE_LESS_THAN_END_DATE}, code=400)

        return data


class RateUsersActivitySerializer(serializers.ModelSerializer):
    student = StudentSerializer(many=False, read_only=True)

    class Meta:
        model = RateActivity
        fields = '__all__'


class CategoriesReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriesReport
        fields = '__all__'


class ReportAbuseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAbuse
        fields = '__all__'


class BoxReportAbuseSerializer(serializers.ModelSerializer):
    category = CategoriesReportSerializer()
    sender = serializers.SerializerMethodField()

    @staticmethod
    def get_sender(obj):
        try:
            return {
                'full_name': obj.sender.first_name + " " + obj.sender.last_name,
                'school': obj.sender.school.name,
                'province': obj.sender.school.province.title,
                'county': obj.sender.school.county.title,
            }
        except:
            return {
                'full_name': obj.sender.first_name + " " + obj.sender.last_name,
                'school_id': "",
                'province': "",
                'county': "",
            }

    class Meta:
        model = ReportAbuse
        fields = ('sender', 'category', 'content')


class ReportAbuseGroupSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    activity_id = serializers.IntegerField()
    count = serializers.IntegerField()
    activity_title = serializers.CharField(source='activity__title')
    school_id = serializers.IntegerField(source='activity__school_id')
    school_name = serializers.CharField(source='activity__school__name')


class ActivityMainSerializer(serializers.ModelSerializer):
    school = SchoolSerializerSadaf(many=False, read_only=True)
    student = StudentSerializer(many=False, read_only=True)
    checker = TeacherSerializer(many=False, read_only=True)

    class Meta:
        model = Activity
        fields = '__all__'
