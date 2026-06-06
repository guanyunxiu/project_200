from rest_framework import serializers
from .models import Student
from apps.users.models import User


class CoachSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'real_name', 'phone']


class StudentSerializer(serializers.ModelSerializer):
    license_type_display = serializers.CharField(source='get_license_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    remaining_hours = serializers.IntegerField(read_only=True)
    coach_info = CoachSimpleSerializer(source='coach', read_only=True)
    package_name = serializers.CharField(source='package.name', read_only=True)

    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'enroll_date']


class StudentSimpleSerializer(serializers.ModelSerializer):
    license_type_display = serializers.CharField(source='get_license_type_display', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'name', 'phone', 'license_type', 'license_type_display', 'remaining_hours']
