from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExamRoomViewSet, ExamScheduleViewSet, ExamBookingViewSet

router = DefaultRouter()
router.register('rooms', ExamRoomViewSet, basename='exam-room')
router.register('schedules', ExamScheduleViewSet, basename='exam-schedule')
router.register('bookings', ExamBookingViewSet, basename='exam-booking')

urlpatterns = [
    path('', include(router.urls)),
]
