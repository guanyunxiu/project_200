from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.db import transaction
from datetime import datetime, date, timedelta
from django.db.models import Sum, Count, Q, F
from .models import Student, HourRecord
from .serializers import StudentSerializer, StudentSimpleSerializer, HourRecordSerializer
from apps.users.permissions import IsAdminOrCoach, IsAdmin, IsFinance
from apps.payments.models import Payment
import uuid


class HourRecordViewSet(viewsets.ModelViewSet):
    queryset = HourRecord.objects.all()
    serializer_class = HourRecordSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrCoach()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role == 'coach':
            queryset = queryset.filter(coach=user)
        student_id = self.request.query_params.get('student_id')
        hour_type = self.request.query_params.get('hour_type')
        operation_type = self.request.query_params.get('operation_type')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if hour_type:
            queryset = queryset.filter(hour_type=hour_type)
        if operation_type:
            queryset = queryset.filter(operation_type=operation_type)
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        return queryset.order_by('-id')

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)

    @action(methods=['post'], detail=False)
    def coach_consume(self, request):
        student_id = request.data.get('student_id')
        hour_type = request.data.get('hour_type', 'practical')
        hours = int(request.data.get('hours', 1))
        coach = request.user
        if coach.role != 'coach':
            return Response({'error': '只有教练可以核销实操课时'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': '学员不存在'}, status=status.HTTP_404_NOT_FOUND)
        if student.coach_id != coach.id:
            return Response({'error': '只能核销自己学员的课时'}, status=status.HTTP_400_BAD_REQUEST)
        if hours <= 0:
            return Response({'error': '核销课时必须大于0'}, status=status.HTTP_400_BAD_REQUEST)
        if hour_type == 'practical' and student.remaining_practical_hours < hours:
            return Response({
                'error': '实操课时不足',
                'remaining': student.remaining_practical_hours
            }, status=status.HTTP_400_BAD_REQUEST)
        if hour_type == 'theory' and student.remaining_theory_hours < hours:
            return Response({
                'error': '理论课时不足',
                'remaining': student.remaining_theory_hours
            }, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            hours_before = student.remaining_practical_hours if hour_type == 'practical' else student.remaining_theory_hours
            if hour_type == 'practical':
                student.used_practical_hours += hours
            else:
                student.used_theory_hours += hours
            student.used_hours += hours
            hours_after = student.remaining_practical_hours if hour_type == 'practical' else student.remaining_theory_hours
            student.save()
            record = HourRecord.objects.create(
                student=student,
                hour_type=hour_type,
                operation_type='consume',
                hours=hours,
                hours_before=hours_before,
                hours_after=hours_after,
                coach=coach,
                operator=coach,
                sign_in_time=datetime.now(),
                remark=request.data.get('remark', '')
            )
            cache.delete(f'student:{student.id}:hours')
            cache.delete(f'student:{student.id}:payment_status')
            need_reminder = student.need_hours_reminder()
        return Response({
            'message': '课时核销成功',
            'record': HourRecordSerializer(record).data,
            'remaining_hours': student.remaining_hours,
            'remaining_practical_hours': student.remaining_practical_hours,
            'remaining_theory_hours': student.remaining_theory_hours,
            'hours_low': student.is_hours_low,
            'need_reminder': need_reminder
        })

    @action(methods=['post'], detail=False)
    def add_theory_hours(self, request):
        student_id = request.data.get('student_id')
        hours = int(request.data.get('hours', 0))
        remark = request.data.get('remark', '')
        if not request.user.role in ['admin', 'coach']:
            return Response({'error': '无权限操作'}, status=status.HTTP_403_FORBIDDEN)
        if hours <= 0:
            return Response({'error': '课时必须大于0'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': '学员不存在'}, status=status.HTTP_404_NOT_FOUND)
        with transaction.atomic():
            hours_before = student.remaining_theory_hours
            student.theory_hours += hours
            student.total_hours += hours
            hours_after = student.remaining_theory_hours
            student.save()
            record = HourRecord.objects.create(
                student=student,
                hour_type='theory',
                operation_type='add',
                hours=hours,
                hours_before=hours_before,
                hours_after=hours_after,
                operator=request.user,
                remark=remark
            )
            cache.delete(f'student:{student.id}:hours')
        return Response({
            'message': '理论课时添加成功',
            'record': HourRecordSerializer(record).data,
            'total_theory_hours': student.theory_hours,
            'remaining_theory_hours': student.remaining_theory_hours
        })

    @action(methods=['post'], detail=False)
    def renew_course(self, request):
        student_id = request.data.get('student_id')
        hours = int(request.data.get('hours', 0))
        hour_type = request.data.get('hour_type', 'practical')
        amount = float(request.data.get('amount', 0))
        payment_method = request.data.get('payment_method', 'wechat')
        remark = request.data.get('remark', '')
        if not request.user.role in ['admin', 'finance']:
            return Response({'error': '无权限操作'}, status=status.HTTP_403_FORBIDDEN)
        if hours <= 0 or amount <= 0:
            return Response({'error': '课时和金额必须大于0'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': '学员不存在'}, status=status.HTTP_404_NOT_FOUND)
        with transaction.atomic():
            hours_before = student.remaining_practical_hours if hour_type == 'practical' else student.remaining_theory_hours
            if hour_type == 'practical':
                student.practical_hours += hours
            else:
                student.theory_hours += hours
            student.total_hours += hours
            hours_after = student.remaining_practical_hours if hour_type == 'practical' else student.remaining_theory_hours
            student.save()
            payment = Payment.objects.create(
                student=student,
                payment_type='course_renewal',
                payment_method=payment_method,
                amount=amount,
                total_amount=amount,
                remaining_amount=0,
                status='confirmed',
                receipt_no=f'RENEW{datetime.now().strftime("%Y%m%d")}{uuid.uuid4().hex[:6].upper()}',
                operator=request.user,
                remark=f'{hour_type == "practical" and "实操" or "理论"}续课{hours}课时 - {remark}'
            )
            record = HourRecord.objects.create(
                student=student,
                hour_type=hour_type,
                operation_type='renewal',
                hours=hours,
                hours_before=hours_before,
                hours_after=hours_after,
                operator=request.user,
                remark=f'续课缴费¥{amount}'
            )
            cache.delete(f'student:{student.id}:hours')
            cache.delete(f'student:{student.id}:payment_status')
        return Response({
            'message': '续课成功',
            'record': HourRecordSerializer(record).data,
            'payment_id': payment.id,
            'total_hours': student.total_hours,
            'remaining_hours': student.remaining_hours
        })

    @action(methods=['get'], detail=False)
    def stats(self, request):
        today = date.today()
        month_start = today.replace(day=1)
        total_records = HourRecord.objects.filter(operation_type='consume').count()
        today_records = HourRecord.objects.filter(
            operation_type='consume',
            created_at__date=today
        ).count()
        total_hours_consumed = HourRecord.objects.filter(
            operation_type='consume'
        ).aggregate(Sum('hours'))['hours__sum'] or 0
        today_hours = HourRecord.objects.filter(
            operation_type='consume',
            created_at__date=today
        ).aggregate(Sum('hours'))['hours__sum'] or 0
        by_type = HourRecord.objects.filter(
            operation_type='consume',
            created_at__date__gte=month_start
        ).values('hour_type').annotate(
            count=Count('id'),
            hours=Sum('hours')
        )
        type_map = {'theory': '理论', 'practical': '实操'}
        type_stats = []
        for item in by_type:
            type_stats.append({
                'hour_type': item['hour_type'],
                'hour_type_name': type_map.get(item['hour_type'], item['hour_type']),
                'count': item['count'],
                'hours': item['hours']
            })
        low_hours_students = Student.objects.filter(
            status='studying'
        ).filter(
            Q(remaining_hours__lte=3) |
            Q(remaining_hours__lte=F('total_hours') * 0.2)
        ).count()
        return Response({
            'total_records': total_records,
            'today_records': today_records,
            'total_hours_consumed': total_hours_consumed,
            'today_hours': today_hours,
            'by_type': type_stats,
            'low_hours_students': low_hours_students
        })


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
            need_reminder = student.need_hours_reminder()
            if need_reminder:
                student.last_hours_reminder = datetime.now()
                student.save()
            cached_data = {
                'total_hours': student.total_hours,
                'used_hours': student.used_hours,
                'remaining_hours': student.remaining_hours,
                'theory_hours': student.theory_hours,
                'used_theory_hours': student.used_theory_hours,
                'remaining_theory_hours': student.remaining_theory_hours,
                'practical_hours': student.practical_hours,
                'used_practical_hours': student.used_practical_hours,
                'remaining_practical_hours': student.remaining_practical_hours,
                'hours_remaining_percent': student.hours_remaining_percent,
                'is_hours_low': student.is_hours_low,
                'is_hours_depleted': student.is_hours_depleted,
                'need_reminder': need_reminder
            }
            cache.set(cache_key, cached_data, timeout=300)
        return Response(cached_data)

    @action(methods=['post'], detail=True)
    def update_hours(self, request, pk=None):
        student = self.get_object()
        hours = int(request.data.get('hours', 0))
        operation = request.data.get('operation', 'add')
        hour_type = request.data.get('hour_type', 'total')
        with transaction.atomic():
            if hour_type == 'total':
                if operation == 'add':
                    student.used_hours += hours
                elif operation == 'subtract':
                    student.used_hours = max(0, student.used_hours - hours)
                elif operation == 'set_total':
                    student.total_hours = hours
            elif hour_type == 'theory':
                if operation == 'add':
                    student.used_theory_hours += hours
                    student.used_hours += hours
                elif operation == 'subtract':
                    student.used_theory_hours = max(0, student.used_theory_hours - hours)
                    student.used_hours = max(0, student.used_hours - hours)
                elif operation == 'set_total':
                    student.theory_hours = hours
                    student.total_hours = student.theory_hours + student.practical_hours
            elif hour_type == 'practical':
                if operation == 'add':
                    student.used_practical_hours += hours
                    student.used_hours += hours
                elif operation == 'subtract':
                    student.used_practical_hours = max(0, student.used_practical_hours - hours)
                    student.used_hours = max(0, student.used_hours - hours)
                elif operation == 'set_total':
                    student.practical_hours = hours
                    student.total_hours = student.theory_hours + student.practical_hours
            student.save()
            cache.delete(f'student:{student.id}:hours')
            cache.delete(f'student:{student.id}:payment_status')
        return Response(StudentSerializer(student).data)

    @action(methods=['get'], detail=True)
    def hour_records(self, request, pk=None):
        student = self.get_object()
        records = student.hour_records.all()[:50]
        return Response(HourRecordSerializer(records, many=True).data)

    @action(methods=['get'], detail=False)
    def low_hours_list(self, request):
        queryset = self.get_queryset().filter(status='studying')
        low_hours_students = []
        for student in queryset:
            if student.is_hours_low:
                low_hours_students.append(student)
        return Response(StudentSerializer(low_hours_students, many=True).data)

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
