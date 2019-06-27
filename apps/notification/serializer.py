from rest_framework import serializers
from apps.notification.models import Notification, FcmTokenUser


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class FcmTokenUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FcmTokenUser
        fields = '__all__'
