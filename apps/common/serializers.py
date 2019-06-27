from rest_framework import serializers

from apps.common.models import File, Image, ApkRelease, ApkChangeRelease, DisableManager


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class ChangeApkReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApkChangeRelease
        fields = ('title', )


class ApkReleaseSerializer(serializers.ModelSerializer):
    @staticmethod
    def _get_address_file(obj):
        try:
            return "/" + obj.file.url
        except:
            return ""

    @staticmethod
    def _get_changed_app_release(obj):
        data = ChangeApkReleaseSerializer(obj.apkchangerelease_set.all(), many=True).data
        list_data = []
        for item in data:
            list_data.append(item["title"])
        return list_data

    file = serializers.SerializerMethodField('_get_address_file')
    change_messages = serializers.SerializerMethodField('_get_changed_app_release')

    class Meta:
        model = ApkRelease
        fields = '__all__'


class DisableManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisableManager
        fields = '__all__'

