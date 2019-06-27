from rest_framework import serializers
from apps.report.models import Reports
from apps.user.models.base import BaseUser
from apps.common.utils import gregorian_to_persian_chart


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseUser
        fields = ("first_name", "last_name", "gender", "phone_number", "last_visit")


class ReportsSerializer(serializers.ModelSerializer):
    @staticmethod
    def get_created_at(obj):
        return gregorian_to_persian_chart(obj.created_at, str_type="%Y/%m/%d %H:%M")

    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Reports
        fields = '__all__'
