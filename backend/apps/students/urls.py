from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, HourRecordViewSet

router = DefaultRouter()
router.register('hours', HourRecordViewSet, basename='hour-record')
router.register('', StudentViewSet, basename='student')

urlpatterns = [
    path('', include(router.urls)),
]
