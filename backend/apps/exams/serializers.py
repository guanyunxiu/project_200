from rest_framework import serializers
from .models import ExamRoom, ExamSchedule, ExamBooking, ExamFeeRule, ExamFee
from apps.students.serializers import StudentSimpleSerializer


class ExamFeeRuleSerializer(serializers.ModelSerializer):
    subject_display = serializers.CharField(source='get_subject_display', read_only=True)

    class Meta:
        model = ExamFeeRule
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExamFeeSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    fee_type_display = serializers.CharField(source='get_fee_type_display', read_only=True)
    subject_display = serializers.CharField(source='get_subject_display', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_phone = serializers.CharField(source='student.phone', read_only=True)
    operator_name = serializers.CharField(source='operator.real_name', read_only=True, allow_null=True)

    class Meta:
        model = ExamFee
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'paid_at', 'operator']


class ExamRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamRoom
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ExamScheduleSerializer(serializers.ModelSerializer):
    subject_display = serializers.CharField(source='get_subject_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    room_name = serializers.CharField(source='exam_room.name', read_only=True)
    room_address = serializers.CharField(source='exam_room.address', read_only=True)
    remaining_quota = serializers.IntegerField(read_only=True)

    class Meta:
        model = ExamSchedule
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'booked_quota']


class ExamScheduleSimpleSerializer(serializers.ModelSerializer):
    subject_display = serializers.CharField(source='get_subject_display', read_only=True)
    room_name = serializers.CharField(source='exam_room.name', read_only=True)

    class Meta:
        model = ExamSchedule
        fields = ['id', 'subject', 'subject_display', 'exam_date', 'start_time', 'end_time', 'room_name', 'total_quota', 'remaining_quota', 'status']


class ExamBookingSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    booking_type_display = serializers.CharField(source='get_booking_type_display', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_phone = serializers.CharField(source='student.phone', read_only=True)
    schedule_info = ExamScheduleSimpleSerializer(source='schedule', read_only=True)
    operator_name = serializers.CharField(source='operator.real_name', read_only=True)

    class Meta:
        model = ExamBooking
        fields = '__all__'
        read_only_fields = ['id', 'booked_at', 'updated_at', 'operator']
