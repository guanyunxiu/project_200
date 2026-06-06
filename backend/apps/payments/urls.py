from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, InstallmentPlanViewSet

router = DefaultRouter()
router.register('', PaymentViewSet, basename='payment')
router.register('installments', InstallmentPlanViewSet, basename='installment')

urlpatterns = [
    path('', include(router.urls)),
]
