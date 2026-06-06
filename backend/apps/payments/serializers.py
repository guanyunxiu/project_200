from rest_framework import serializers
from .models import Payment, InstallmentPlan, InstallmentRecord
from apps.students.serializers import StudentSimpleSerializer


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

    class Meta:
        model = InstallmentRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class InstallmentPlanSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_phone = serializers.CharField(source='student.phone', read_only=True)
    records = InstallmentRecordSerializer(many=True, read_only=True)

    class Meta:
        model = InstallmentPlan
        fields = '__all__'
        read_only_fields = ['id', 'paid_amount', 'remaining_amount', 'status', 'created_at', 'updated_at']


class StudentPaymentSummarySerializer(serializers.Serializer):
    student = StudentSimpleSerializer(read_only=True)
    total_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_due = serializers.DecimalField(max_digits=10, decimal_places=2)
    remaining = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_status = serializers.CharField()
    last_payment_date = serializers.DateField(allow_null=True)
