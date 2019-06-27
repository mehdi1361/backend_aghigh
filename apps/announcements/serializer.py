from rest_framework import serializers
from django.contrib.auth.models import User
from apps.announcements.models import (
    AnnouncementReceiver,
    Announcement,
    AnnouncementFile,
    AnnouncementSeenHistory
)


class AnnouncementCreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class AnnouncementUrlField(serializers.HyperlinkedModelSerializer):
    def to_representation(self, value):
        return '/' + value.url

    def to_internal_value(self, data):
        pass


class AnnouncementFilesSerializer(serializers.ModelSerializer):
    file = AnnouncementUrlField(read_only=True)

    class Meta:
        model = AnnouncementFile
        fields = ('id', 'title', 'file', 'size', 'duration')


class AnnouncementReceiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementReceiver
        fields = '__all__'


class DetailAnnouncementReceiverSerializer(serializers.ModelSerializer):

    @staticmethod
    def _get_display_user_type(obj):
        return obj.get_user_type_display()

    @staticmethod
    def _get_display_gender(obj):
        return obj.get_gender_display()

    display_user_type = serializers.SerializerMethodField('_get_display_user_type')
    display_gender = serializers.SerializerMethodField('_get_display_gender')

    class Meta:
        model = AnnouncementReceiver
        fields = (
            'id',
            'display_user_type',
            'user_type',
            'province',
            'county',
            'camp',
            'school',
            'created_at',
            'updated_at',
            'gender',
            'display_gender'
        )
        depth = 1


class AnnouncementSeenHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementSeenHistory
        fields = '__all__'


class AnnouncementSerializer(serializers.ModelSerializer):
    def get_user(self):
        r = self.context["request"]
        return r.user

    def is_seen(self, obj):

        user = self.get_user()

        is_seen = AnnouncementSeenHistory.objects.filter(user=user, announcement=obj)
        if is_seen.exists():
            return True
        else:
            return False

    @staticmethod
    def get_image_url(obj):
        try:
            return "/" + obj.image.url
        except:
            return ""

    @staticmethod
    def _get_image_info(obj):
        try:
            if obj.image:
                image_info = dict(
                    title=obj.image.name,
                    size=obj.image.size,
                    url="/" + obj.image.url
                )
            else:
                image_info = {}
            return image_info
        except:
            return {}

    files = AnnouncementFilesSerializer(many=True, source='get_files')
    image = serializers.SerializerMethodField('get_image_url')
    image_info = serializers.SerializerMethodField('_get_image_info')
    creator = AnnouncementCreatorSerializer(read_only=True)
    seen = serializers.SerializerMethodField('is_seen')

    class Meta:
        model = Announcement
        fields = (
            'id',
            'title',
            'description',
            'creator',
            'seen',
            'image',
            'image_info',
            'files',
            'created_at',
            'release_time',
            'has_date',
            'date',
            'view_count'
        )
