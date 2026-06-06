from rest_framework import serializers
from .models import Payment, InstallmentPlan, InstallmentRecord, InstallmentScheme, PaymentReminder
from apps.students.serializers import StudentSimpleSerializer


class InstallmentSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentScheme
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentReminderSerializer(serializers.ModelSerializer):
    reminder_type_display = serializers.CharField(source='get_reminder_type_display', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_phone = serializers.CharField(source='student.phone', read_only=True)
    operator_name = serializers.CharField(source='operator.real_name', read_only=True)

    class Meta:
        model = PaymentReminder
        fields = '__all__'
        read_only_fields = ['id', 'reminder_date', 'created_at', 'operator']


class PaymentSerializer(serializers.ModelSerializer):
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_phone = serializers.CharField(source='student.phone', read_only=True)
    package_name = serializers.CharField(source='package.name', read_only=True)
    operator_name = serializers.CharField(source='operator.real_name', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['id', 'receipt_no', 'created_at', 'updated_at', 'operator']


class InstallmentRecordSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_amount_due = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = InstallmentRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'late_fee', 'late_fee_days']


class InstallmentPlanSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_phone = serializers.CharField(source='student.phone', read_only=True)
    scheme_name = serializers.CharField(source='scheme.name', read_only=True, allow_null=True)
    records = InstallmentRecordSerializer(many=True, read_only=True)
    reminders = PaymentReminderSerializer(many=True, read_only=True)

    class Meta:
        model = InstallmentPlan
        fields = '__all__'
        read_only_fields = ['id', 'paid_amount', 'remaining_amount', 'status', 'total_late_fee', 'created_at', 'updated_at']


class StudentPaymentSummarySerializer(serializers.Serializer):
    student = StudentSimpleSerializer(read_only=True)
    total_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_due = serializers.DecimalField(max_digits=10, decimal_places=2)
    remaining = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_status = serializers.CharField()
    last_payment_date = serializers.DateField(allow_null=True)
