from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from apps.students.models import Student


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'real_name', 'phone', 'email', 'role', 'role_display', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'password', 'real_name', 'phone', 'email', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(**attrs)
        if not user:
            raise serializers.ValidationError('用户名或密码错误')
        if not user.is_active:
            raise serializers.ValidationError('账号已被禁用')
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=6)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密码错误')
        return value


class StudentRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3, max_length=50)
    password = serializers.CharField(write_only=True, min_length=6)
    name = serializers.CharField(max_length=50)
    gender = serializers.ChoiceField(choices=Student.GENDER_CHOICES)
    phone = serializers.CharField(max_length=20)
    id_card = serializers.CharField(max_length=18)
    license_type = serializers.ChoiceField(choices=Student.LICENSE_TYPE_CHOICES)
    birthday = serializers.DateField()
    address = serializers.CharField(max_length=200, required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('用户名已存在')
        return value

    def validate_phone(self, value):
        if Student.objects.filter(phone=value).exists():
            raise serializers.ValidationError('手机号已注册')
        return value

    def validate_id_card(self, value):
        if Student.objects.filter(id_card=value).exists():
            raise serializers.ValidationError('身份证号已注册')
        return value

    def create(self, validated_data):
        user_data = {
            'username': validated_data['username'],
            'real_name': validated_data['name'],
            'phone': validated_data['phone'],
            'role': 'student',
            'is_active': True
        }
        password = validated_data.pop('password')
        user = User(**user_data)
        user.set_password(password)
        user.save()

        student_data = {
            'name': validated_data['name'],
            'gender': validated_data['gender'],
            'phone': validated_data['phone'],
            'id_card': validated_data['id_card'],
            'license_type': validated_data['license_type'],
            'birthday': validated_data['birthday'],
            'address': validated_data.get('address', ''),
            'status': 'studying'
        }
        student = Student.objects.create(user=user, **student_data)
        return user, student
