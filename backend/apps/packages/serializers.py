from rest_framework import serializers
from .models import Package


class PackageSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    license_type_display = serializers.CharField(source='get_license_type_display', read_only=True)
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    student_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Package
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class PackageSimpleSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Package
        fields = ['id', 'name', 'code', 'type', 'type_display', 'base_price', 'total_hours', 'is_active']
