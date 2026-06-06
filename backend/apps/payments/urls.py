from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PaymentViewSet, InstallmentPlanViewSet,
    InstallmentSchemeViewSet, PaymentReminderViewSet,
    FinancialStatsViewSet
)

router = DefaultRouter()
router.register('schemes', InstallmentSchemeViewSet, basename='installment-scheme')
router.register('reminders', PaymentReminderViewSet, basename='payment-reminder')
router.register('installments', InstallmentPlanViewSet, basename='installment')
router.register('stats', FinancialStatsViewSet, basename='financial-stats')
router.register('', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]
