from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from .models import Package
from .serializers import PackageSerializer, PackageSimpleSerializer
from apps.users.permissions import IsAdmin


class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset().annotate(student_count=Count('students'))
        is_active = self.request.query_params.get('is_active')
        type = self.request.query_params.get('type')
        license_type = self.request.query_params.get('license_type')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if type:
            queryset = queryset.filter(type=type)
        if license_type:
            queryset = queryset.filter(license_type__in=[license_type, 'all'])
        return queryset.order_by('-id')

    @action(methods=['get'], detail=False)
    def active_list(self, request):
        queryset = self.get_queryset().filter(is_active=True)
        serializer = PackageSimpleSerializer(queryset, many=True)
        return Response(serializer.data)
