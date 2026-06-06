from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExamRoomViewSet, ExamScheduleViewSet, ExamBookingViewSet,
    ExamFeeRuleViewSet, ExamFeeViewSet
)

router = DefaultRouter()
router.register('fee-rules', ExamFeeRuleViewSet, basename='exam-fee-rule')
router.register('fees', ExamFeeViewSet, basename='exam-fee')
router.register('rooms', ExamRoomViewSet, basename='exam-room')
router.register('schedules', ExamScheduleViewSet, basename='exam-schedule')
router.register('bookings', ExamBookingViewSet, basename='exam-booking')

urlpatterns = [
    path('', include(router.urls)),
]
