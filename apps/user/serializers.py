from rest_framework import serializers
from apps.league import models
from apps.user.models import student
from apps.user.models.base import BaseUser, UserSession
from apps.user.models.teacher import Teacher
from datetime import datetime, timedelta


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.School
        fields = (
            'id',
            'name',
            'province',
            'county',
        )
        depth = 1


class StudentSerializer(serializers.ModelSerializer):
    school = SchoolSerializer(many=False, read_only=True)

    class Meta:
        model = student.Student
        fields = (
            'id',
            'first_name',
            'last_name',
            'school',
            'gender',
        )


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = (
            'id',
            'first_name',
            'last_name',
            'phone_number',
            'gender',
            'email',
        )


class SchoolSerializerSadaf(serializers.ModelSerializer):
    teacher = TeacherSerializer(many=False, read_only=True)

    class Meta:
        model = models.School
        fields = (
            'id',
            'name',
            'province',
            'county',
            'teacher',
        )
        depth = 1


class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseUser
        fields = (
            'id',
            'first_name',
            'last_name',
            'phone_number',
            'gender',
            'email',
            'image',
        )


class UserSessionSerializer(serializers.ModelSerializer):
    state = serializers.SerializerMethodField()

    class Meta:
        model = UserSession
        fields = (
            'user_name',
            'name',
            'role',
            'created_date',
            'updated_date',
            'last_login_date',
            'state',
        )

    def get_state(self, obj):
        return datetime.now() - obj.updated_date < timedelta(seconds=600)
