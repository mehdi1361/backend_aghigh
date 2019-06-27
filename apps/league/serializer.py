from rest_framework import serializers

from apps.activity.models import Activity
from apps.league.models import School, Province, County, Camp
from apps.user.serializers import TeacherSerializer
from apps.user.models.student import Student


class UrlSchoolImage(serializers.HyperlinkedModelSerializer):
    def to_representation(self, value):
        try:
            image_url = '/' + value.url
        except:
            image_url = None
        return image_url

    def to_internal_value(self, data):
        pass


class LeagueSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer()
    image = UrlSchoolImage(read_only=True)

    @staticmethod
    def get_count_all_activity_acc(obj):
        return Activity.objects.filter(
            state="ACCEPT",
            school_id=obj.id
        ).count()

    count_in_queue_acc = serializers.SerializerMethodField('get_count_all_activity_acc')

    class Meta:
        model = School
        depth = 1
        fields = (
            'id', 'name', 'gender', 'active', 'teacher',
            'camp', 'county', 'province', 'student_count',
            'anjoman_count', 'point', 'rank', 'image',
            'province_rank', 'county_rank', 'voters',
            'count_in_queue_acc'
        )


class SchoolTeacherSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer()

    @staticmethod
    def get_count_all_activity_shr(obj):
        return Activity.objects.filter(
            state__in=["SHR", 'NEW'],  # TODO چرا نیو حذف شده بود بررسی شود
            school_id=obj.id
        ).count()

    @staticmethod
    def get_count_all_activity_she(obj):
        return Activity.objects.filter(
            state="SHE",
            school_id=obj.id
        ).count()

    @staticmethod
    def get_count_all_activity_acc(obj):
        return Activity.objects.filter(
            state="ACCEPT",
            school_id=obj.id,
        ).count()

    count_in_queue_she = serializers.SerializerMethodField('get_count_all_activity_she')
    count_in_queue_shr = serializers.SerializerMethodField('get_count_all_activity_shr')
    count_in_queue_acc = serializers.SerializerMethodField('get_count_all_activity_acc')

    class Meta:
        model = School
        depth = 1
        fields = (
            'id', 'name', 'gender', 'active', 'teacher',
            'camp', 'county', 'province', 'student_count',
            'anjoman_count', 'point', 'rank', 'image',
            'province_rank', 'county_rank', 'voters',
            'count_in_queue_she', 'count_in_queue_shr', 'count_in_queue_acc'
        )


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = '__all__'


class CountySerializer(serializers.ModelSerializer):
    class Meta:
        model = County
        fields = '__all__'


class CampSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camp
        fields = '__all__'


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'


class OtherSchoolSerializer(serializers.ModelSerializer):
    image = UrlSchoolImage(read_only=True)

    @staticmethod
    def _get_student_name(obj):
        student = Student.objects.filter(school_id=obj.id)
        if student.exists():
            return student[0].first_name + " " + student[0].last_name
        return ""

    student_name = serializers.SerializerMethodField('_get_student_name')

    class Meta:
        model = School
        depth = 1
        fields = (
            "name",
            "gender",
            "active",
            "province",
            "county",
            "point",
            "rank",
            "province_rank",
            "county_rank",
            "student_name",
            "voters",
            "image",
        )
