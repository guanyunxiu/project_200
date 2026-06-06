from rest_framework import serializers
from .models import Student, HourRecord
from apps.users.models import User


class CoachSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'real_name', 'phone']


class HourRecordSerializer(serializers.ModelSerializer):
    hour_type_display = serializers.CharField(source='get_hour_type_display', read_only=True)
    operation_type_display = serializers.CharField(source='get_operation_type_display', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)
    coach_name = serializers.CharField(source='coach.real_name', read_only=True, allow_null=True)
    operator_name = serializers.CharField(source='operator.real_name', read_only=True, allow_null=True)

    class Meta:
        model = HourRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'hours_before', 'hours_after', 'operator']


class StudentSerializer(serializers.ModelSerializer):
    license_type_display = serializers.CharField(source='get_license_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    remaining_hours = serializers.IntegerField(read_only=True)
    remaining_theory_hours = serializers.IntegerField(read_only=True)
    remaining_practical_hours = serializers.IntegerField(read_only=True)
    hours_remaining_percent = serializers.FloatField(read_only=True)
    is_hours_low = serializers.BooleanField(read_only=True)
    is_hours_depleted = serializers.BooleanField(read_only=True)
    coach_info = CoachSimpleSerializer(source='coach', read_only=True)
    package_name = serializers.CharField(source='package.name', read_only=True)

    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'enroll_date', 'used_hours', 'used_theory_hours', 'used_practical_hours']


class StudentSimpleSerializer(serializers.ModelSerializer):
    license_type_display = serializers.CharField(source='get_license_type_display', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'name', 'phone', 'license_type', 'license_type_display', 'remaining_hours']
