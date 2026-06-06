from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.cache import cache
from django.db import transaction
from datetime import datetime, date
from .models import ExamRoom, ExamSchedule, ExamBooking
from .serializers import (
    ExamRoomSerializer, ExamScheduleSerializer,
    ExamScheduleSimpleSerializer, ExamBookingSerializer
)
from apps.users.permissions import IsAdmin, IsAdminOrCoach


class ExamRoomViewSet(viewsets.ModelViewSet):
    queryset = ExamRoom.objects.all()
    serializer_class = ExamRoomSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset


class ExamScheduleViewSet(viewsets.ModelViewSet):
    queryset = ExamSchedule.objects.all()
    serializer_class = ExamScheduleSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'lock_quota', 'unlock_quota']:
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        subject = self.request.query_params.get('subject')
        exam_room_id = self.request.query_params.get('exam_room_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        status = self.request.query_params.get('status')
        if subject:
            queryset = queryset.filter(subject=subject)
        if exam_room_id:
            queryset = queryset.filter(exam_room_id=exam_room_id)
        if start_date:
            queryset = queryset.filter(exam_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(exam_date__lte=end_date)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    @action(methods=['get'], detail=False, permission_classes=[AllowAny])
    def available_list(self, request):
        today = date.today()
        queryset = self.get_queryset().filter(
            status='open',
            exam_date__gte=today
        ).order_by('exam_date', 'start_time')
        serializer = ExamScheduleSimpleSerializer(queryset, many=True)
        for item in serializer.data:
            cache_key = f'exam:{item["id"]}:quota'
            cached = cache.get(cache_key)
            if cached:
                item['remaining_quota'] = cached['remaining']
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def lock_quota(self, request, pk=None):
        schedule = self.get_object()
        schedule.status = 'locked'
        schedule.save()
        cache.delete(f'exam:{schedule.id}:quota')
        return Response(ExamScheduleSerializer(schedule).data)

    @action(methods=['post'], detail=True)
    def unlock_quota(self, request, pk=None):
        schedule = self.get_object()
        schedule.status = 'open'
        schedule.save()
        cache.delete(f'exam:{schedule.id}:quota')
        return Response(ExamScheduleSerializer(schedule).data)

    @action(methods=['get'], detail=True)
    def quota_cache(self, request, pk=None):
        schedule = self.get_object()
        cache_key = f'exam:{schedule.id}:quota'
        cached = cache.get(cache_key)
        if not cached:
            cached = {
                'total': schedule.total_quota,
                'booked': schedule.booked_quota,
                'remaining': schedule.remaining_quota
            }
            cache.set(cache_key, cached, timeout=300)
        return Response(cached)

    @action(methods=['get'], detail=False)
    def stats(self, request):
        today = date.today()
        total_schedules = ExamSchedule.objects.count()
        open_schedules = ExamSchedule.objects.filter(status='open').count()
        today_exams = ExamSchedule.objects.filter(exam_date=today).count()
        total_bookings = ExamBooking.objects.filter(status='approved').count()
        return Response({
            'total_schedules': total_schedules,
            'open_schedules': open_schedules,
            'today_exams': today_exams,
            'total_bookings': total_bookings
        })


class ExamBookingViewSet(viewsets.ModelViewSet):
    queryset = ExamBooking.objects.all()
    serializer_class = ExamBookingSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [IsAdminOrCoach()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        if self.action in ['self_book']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role == 'coach':
            queryset = queryset.filter(student__coach=user)
        student_id = self.request.query_params.get('student_id')
        schedule_id = self.request.query_params.get('schedule_id')
        subject = self.request.query_params.get('subject')
        status = self.request.query_params.get('status')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if schedule_id:
            queryset = queryset.filter(schedule_id=schedule_id)
        if subject:
            queryset = queryset.filter(schedule__subject=subject)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        booking = serializer.save(
            operator=self.request.user,
            booking_type='admin'
        )
        self._update_schedule_quota(booking.schedule, 1)
        if booking.status == 'approved':
            self._update_schedule_quota(booking.schedule, 1)

    def _update_schedule_quota(self, schedule, delta):
        cache_key = f'exam:{schedule.id}:quota'
        cache.delete(cache_key)
        schedule.booked_quota += delta
        schedule.save()
        cache.set(cache_key, {
            'total': schedule.total_quota,
            'booked': schedule.booked_quota,
            'remaining': schedule.remaining_quota
        }, timeout=300)

    @action(methods=['post'], detail=False)
    def self_book(self, request):
        student_id = request.data.get('student_id')
        schedule_id = request.data.get('schedule_id')
        if not student_id or not schedule_id:
            return Response({'error': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)
        from apps.students.models import Student
        student = Student.objects.filter(id=student_id, phone=request.data.get('phone')).first()
        if not student:
            return Response({'error': '学员信息错误'}, status=status.HTTP_400_BAD_REQUEST)
        schedule = ExamSchedule.objects.filter(id=schedule_id, status='open').first()
        if not schedule:
            return Response({'error': '该考试不开放预约'}, status=status.HTTP_400_BAD_REQUEST)
        cache_key = f'exam:{schedule.id}:quota'
        cached = cache.get(cache_key)
        if cached and cached['remaining'] <= 0:
            return Response({'error': '名额已满'}, status=status.HTTP_400_BAD_REQUEST)
        if schedule.remaining_quota <= 0:
            return Response({'error': '名额已满'}, status=status.HTTP_400_BAD_REQUEST)
        if ExamBooking.objects.filter(student=student, schedule=schedule).exists():
            return Response({'error': '已预约该考试'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            booking = ExamBooking.objects.create(
                student=student,
                schedule=schedule,
                status='pending',
                booking_type='self',
                remark='学员自主约考'
            )
            self._update_schedule_quota(schedule, 1)
        return Response(ExamBookingSerializer(booking).data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True)
    def approve(self, request, pk=None):
        booking = self.get_object()
        if booking.status != 'pending':
            return Response({'error': '只能审核待审核的预约'}, status=status.HTTP_400_BAD_REQUEST)
        booking.status = 'approved'
        booking.save()
        return Response(ExamBookingSerializer(booking).data)

    @action(methods=['post'], detail=True)
    def mark_absent(self, request, pk=None):
        booking = self.get_object()
        booking.status = 'absent'
        booking.save()
        return Response(ExamBookingSerializer(booking).data)

    @action(methods=['post'], detail=True)
    def mark_result(self, request, pk=None):
        booking = self.get_object()
        passed = request.data.get('passed', False)
        score = request.data.get('score')
        booking.status = 'passed' if passed else 'failed'
        if score is not None:
            booking.score = int(score)
        booking.save()
        return Response(ExamBookingSerializer(booking).data)

    @action(methods=['post'], detail=True)
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status in ['passed', 'failed', 'absent']:
            return Response({'error': '该状态下不能取消'}, status=status.HTTP_400_BAD_REQUEST)
        schedule = booking.schedule
        booking.status = 'cancelled'
        booking.save()
        self._update_schedule_quota(schedule, -1)
        return Response(ExamBookingSerializer(booking).data)
