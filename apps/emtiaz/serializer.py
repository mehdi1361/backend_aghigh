from rest_framework import serializers
from apps.emtiaz.models import Param, ActivityComment, ParamActivityComment, SumActivityParam
from apps.user.serializers import StudentSerializer


class ParamActivityCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParamActivityComment
        fields = ('param', 'value')
        depth = 2


class CreateActivityCommentSerializer(serializers.ModelSerializer):
    params = ParamActivityCommentSerializer(many=True, read_only=True, source='get_param')

    class Meta:
        model = ActivityComment
        fields = ('id', 'create_at', 'comment', 'status', 'activity', 'sender', 'params')


class ShowCommentSerializer(serializers.ModelSerializer):
    params = ParamActivityCommentSerializer(many=True, read_only=True, source='get_param')
    sender = StudentSerializer(many=False, read_only=True)

    class Meta:
        model = ActivityComment
        fields = ('id', 'create_at', 'comment', 'status', 'activity', 'sender', 'params')


class ParamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Param
        fields = '__all__'


class SumActivityParamSerializer(serializers.ModelSerializer):
    class Meta:
        model = SumActivityParam
        fields = '__all__'
