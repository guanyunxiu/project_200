from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from .models import Student
from .serializers import StudentSerializer, StudentSimpleSerializer
from apps.users.permissions import IsAdminOrCoach


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrCoach()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role == 'coach':
            queryset = queryset.filter(coach=user)
        name = self.request.query_params.get('name')
        phone = self.request.query_params.get('phone')
        license_type = self.request.query_params.get('license_type')
        status = self.request.query_params.get('status')
        coach_id = self.request.query_params.get('coach_id')
        if name:
            queryset = queryset.filter(name__icontains=name)
        if phone:
            queryset = queryset.filter(phone__icontains=phone)
        if license_type:
            queryset = queryset.filter(license_type=license_type)
        if status:
            queryset = queryset.filter(status=status)
        if coach_id:
            queryset = queryset.filter(coach_id=coach_id)
        return queryset

    @action(methods=['get'], detail=False)
    def simple_list(self, request):
        queryset = self.get_queryset().filter(status='studying')
        serializer = StudentSimpleSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def hours_cache(self, request, pk=None):
        student = self.get_object()
        cache_key = f'student:{student.id}:hours'
        cached_data = cache.get(cache_key)
        if not cached_data:
            cached_data = {
                'total_hours': student.total_hours,
                'used_hours': student.used_hours,
                'remaining_hours': student.remaining_hours
            }
            cache.set(cache_key, cached_data, timeout=300)
        return Response(cached_data)

    @action(methods=['post'], detail=True)
    def update_hours(self, request, pk=None):
        student = self.get_object()
        hours = int(request.data.get('hours', 0))
        operation = request.data.get('operation', 'add')
        if operation == 'add':
            student.used_hours += hours
        elif operation == 'subtract':
            student.used_hours = max(0, student.used_hours - hours)
        elif operation == 'set_total':
            student.total_hours = hours
        student.save()
        cache.delete(f'student:{student.id}:hours')
        cache.delete(f'student:{student.id}:payment_status')
        return Response(StudentSerializer(student).data)

    @action(methods=['post'], detail=True)
    def bind_coach(self, request, pk=None):
        student = self.get_object()
        coach_id = request.data.get('coach_id')
        if coach_id:
            from apps.users.models import User
            coach = User.objects.filter(id=coach_id, role='coach').first()
            if coach:
                student.coach = coach
                student.save()
                return Response(StudentSerializer(student).data)
        return Response({'error': '教练不存在'}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False)
    def stats(self, request):
        total = Student.objects.count()
        studying = Student.objects.filter(status='studying').count()
        graduated = Student.objects.filter(status='graduated').count()
        by_license = {
            'C1': Student.objects.filter(license_type='C1').count(),
            'C2': Student.objects.filter(license_type='C2').count(),
            'D': Student.objects.filter(license_type='D').count(),
        }
        return Response({
            'total': total,
            'studying': studying,
            'graduated': graduated,
            'by_license': by_license
        })
