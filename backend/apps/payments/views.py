from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.core.cache import cache
from django.db.models import Sum, Q
from datetime import datetime, timedelta
import uuid
from openpyxl import Workbook
from .models import Payment, InstallmentPlan, InstallmentRecord
from .serializers import (
    PaymentSerializer, InstallmentPlanSerializer,
    InstallmentRecordSerializer, StudentPaymentSummarySerializer
)
from apps.users.permissions import IsAdminOrFinance, IsAdmin


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrFinance()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get('student_id')
        payment_type = self.request.query_params.get('payment_type')
        payment_method = self.request.query_params.get('payment_method')
        status = self.request.query_params.get('status')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if payment_type:
            queryset = queryset.filter(payment_type=payment_type)
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        if status:
            queryset = queryset.filter(status=status)
        if start_date:
            queryset = queryset.filter(paid_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(paid_at__date__lte=end_date)
        return queryset.order_by('-id')

    def perform_create(self, serializer):
        receipt_no = f'PAY{datetime.now().strftime("%Y%m%d")}{uuid.uuid4().hex[:6].upper()}'
        serializer.save(operator=self.request.user, receipt_no=receipt_no)
        student = serializer.instance.student
        cache.delete(f'student:{student.id}:payment_status')
        if serializer.instance.payment_type == 'installment':
            self._update_installment_record(serializer.instance)

    def _update_installment_record(self, payment):
        if payment.installment_no > 0:
            record = InstallmentRecord.objects.filter(
                plan__student=payment.student,
                period=payment.installment_no,
                status='unpaid'
            ).first()
            if record:
                record.status = 'paid'
                record.paid_date = datetime.now().date()
                record.payment = payment
                record.save()
                plan = record.plan
                plan.paid_amount += payment.amount
                plan.remaining_amount = plan.total_amount - plan.down_payment - plan.paid_amount
                if plan.remaining_amount <= 0:
                    plan.status = 'paid'
                plan.save()

    @action(methods=['get'], detail=False)
    def export_excel(self, request):
        queryset = self.get_queryset()
        wb = Workbook()
        ws = wb.active
        ws.title = '缴费记录'
        headers = ['凭证号', '学员姓名', '手机号', '套餐', '缴费类型', '支付方式', '金额', '总金额', '剩余未缴', '状态', '经办人', '缴费时间', '备注']
        ws.append(headers)
        for p in queryset:
            ws.append([
                p.receipt_no,
                p.student.name,
                p.student.phone,
                p.package.name if p.package else '',
                p.get_payment_type_display(),
                p.get_payment_method_display(),
                float(p.amount),
                float(p.total_amount),
                float(p.remaining_amount),
                p.get_status_display(),
                p.operator.real_name if p.operator else '',
                p.paid_at.strftime('%Y-%m-%d %H:%M:%S') if p.paid_at else '',
                p.remark or ''
            ])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=payments_{datetime.now().strftime("%Y%m%d")}.xlsx'
        wb.save(response)
        return response

    @action(methods=['get'], detail=False)
    def student_summary(self, request):
        from apps.students.models import Student
        students = Student.objects.all()
        summary_list = []
        for student in students:
            cache_key = f'student:{student.id}:payment_status'
            cached = cache.get(cache_key)
            if cached:
                summary_list.append(cached)
                continue
            payments = student.payments.filter(status='confirmed')
            total_paid = payments.aggregate(Sum('amount'))['amount__sum'] or 0
            total_due = payments.first().total_amount if payments.first() else 0
            remaining = total_due - total_paid
            if remaining <= 0:
                payment_status = '已缴清'
            elif total_paid == 0:
                payment_status = '未缴费'
            else:
                payment_status = '部分缴费'
            last_payment = payments.order_by('-paid_at').first()
            data = {
                'student': student,
                'total_paid': total_paid,
                'total_due': total_due,
                'remaining': remaining,
                'payment_status': payment_status,
                'last_payment_date': last_payment.paid_at.date() if last_payment else None
            }
            cache.set(cache_key, data, timeout=600)
            summary_list.append(data)
        serializer = StudentPaymentSummarySerializer(summary_list, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def stats(self, request):
        today = datetime.now().date()
        month_start = today.replace(day=1)
        today_total = Payment.objects.filter(
            status='confirmed', paid_at__date=today
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        month_total = Payment.objects.filter(
            status='confirmed', paid_at__date__gte=month_start
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        total_count = Payment.objects.filter(status='confirmed').count()
        pending_count = Payment.objects.filter(status='pending').count()
        return Response({
            'today_total': float(today_total),
            'month_total': float(month_total),
            'total_count': total_count,
            'pending_count': pending_count
        })


class InstallmentPlanViewSet(viewsets.ModelViewSet):
    queryset = InstallmentPlan.objects.all()
    serializer_class = InstallmentPlanSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrFinance()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get('student_id')
        status = self.request.query_params.get('status')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-id')

    def perform_create(self, serializer):
        plan = serializer.save()
        self._create_installment_records(plan)

    def _create_installment_records(self, plan):
        from dateutil.relativedelta import relativedelta
        for period in range(1, plan.months + 1):
            due_date = plan.start_date + relativedelta(months=period)
            InstallmentRecord.objects.create(
                plan=plan,
                period=period,
                amount=plan.monthly_amount,
                due_date=due_date,
                status='unpaid'
            )

    @action(methods=['post'], detail=True)
    def pay_period(self, request, pk=None):
        plan = self.get_object()
        period = int(request.data.get('period', 0))
        record = plan.records.filter(period=period, status='unpaid').first()
        if not record:
            return Response({'error': '该期次不存在或已还款'}, status=status.HTTP_400_BAD_REQUEST)
        payment_data = {
            'student': plan.student_id,
            'payment_type': 'installment',
            'payment_method': request.data.get('payment_method', 'wechat'),
            'amount': record.amount,
            'total_amount': plan.total_amount,
            'remaining_amount': plan.remaining_amount - record.amount,
            'installment_no': period,
            'status': 'confirmed'
        }
        serializer = PaymentSerializer(data=payment_data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'message': '还款成功', 'payment': serializer.data})

    @action(methods=['get'], detail=False)
    def overdue_list(self, request):
        today = datetime.now().date()
        overdue_records = InstallmentRecord.objects.filter(
            status='unpaid',
            due_date__lt=today
        ).select_related('plan', 'plan__student')
        for record in overdue_records:
            record.status = 'overdue'
            record.save()
        plans = InstallmentPlan.objects.filter(
            records__status='overdue'
        ).distinct()
        return Response(InstallmentPlanSerializer(plans, many=True).data)
