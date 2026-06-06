from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.core.cache import cache
from django.db.models import Sum, Q, Count, Case, When, IntegerField, F
from datetime import datetime, timedelta, date
import uuid
from openpyxl import Workbook
from .models import Payment, InstallmentPlan, InstallmentRecord, InstallmentScheme, PaymentReminder
from .serializers import (
    PaymentSerializer, InstallmentPlanSerializer,
    InstallmentRecordSerializer, StudentPaymentSummarySerializer,
    InstallmentSchemeSerializer, PaymentReminderSerializer
)
from apps.users.permissions import IsAdminOrFinance, IsAdmin
from apps.exams.models import ExamFee


class InstallmentSchemeViewSet(viewsets.ModelViewSet):
    queryset = InstallmentScheme.objects.all()
    serializer_class = InstallmentSchemeSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset.order_by('-id')

    @action(methods=['get'], detail=False)
    def active_list(self, request):
        queryset = self.get_queryset().filter(is_active=True)
        return Response(InstallmentSchemeSerializer(queryset, many=True).data)


class PaymentReminderViewSet(viewsets.ModelViewSet):
    queryset = PaymentReminder.objects.all()
    serializer_class = PaymentReminderSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrFinance()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get('student_id')
        installment_plan_id = self.request.query_params.get('installment_plan_id')
        result = self.request.query_params.get('result')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if installment_plan_id:
            queryset = queryset.filter(installment_plan_id=installment_plan_id)
        if result:
            queryset = queryset.filter(result=result)
        if start_date:
            queryset = queryset.filter(reminder_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(reminder_date__lte=end_date)
        return queryset.order_by('-id')

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)


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
    def calculate_late_fees(self, request, pk=None):
        plan = self.get_object()
        for record in plan.records.filter(status='unpaid'):
            record.calculate_late_fee()
        plan.update_overdue_status()
        return Response({'message': '滞纳金计算完成', 'total_late_fee': float(plan.total_late_fee)})

    @action(methods=['post'], detail=True)
    def pay_period(self, request, pk=None):
        plan = self.get_object()
        period = int(request.data.get('period', 0))
        record = plan.records.filter(period=period, status__in=['unpaid', 'overdue']).first()
        if not record:
            return Response({'error': '该期次不存在或已还款'}, status=status.HTTP_400_BAD_REQUEST)
        record.calculate_late_fee()
        total_amount = float(record.amount) + float(record.late_fee)
        payment_data = {
            'student': plan.student_id,
            'payment_type': 'installment',
            'payment_method': request.data.get('payment_method', 'wechat'),
            'amount': total_amount,
            'total_amount': plan.total_amount,
            'remaining_amount': plan.remaining_amount - float(record.amount),
            'installment_no': period,
            'status': 'confirmed'
        }
        if plan.package_id:
            payment_data['package'] = plan.package_id
        serializer = PaymentSerializer(data=payment_data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        payment_view = PaymentViewSet()
        payment_view.request = request
        payment_view.perform_create(serializer)
        return Response({'message': '还款成功', 'payment': serializer.data, 'late_fee': float(record.late_fee)})

    @action(methods=['get'], detail=False)
    def overdue_list(self, request):
        today = datetime.now().date()
        overdue_records = InstallmentRecord.objects.filter(
            status__in=['unpaid', 'overdue'],
            due_date__lt=today
        ).select_related('plan', 'plan__student')
        for record in overdue_records:
            record.status = 'overdue'
            record.calculate_late_fee()
            record.save()
        plans = InstallmentPlan.objects.filter(
            records__status='overdue'
        ).distinct()
        return Response(InstallmentPlanSerializer(plans, many=True).data)

    @action(methods=['get'], detail=False)
    def arrears_ledger(self, request):
        today = date.today()
        unpaid_records = InstallmentRecord.objects.filter(
            status__in=['unpaid', 'overdue']
        ).select_related('plan', 'plan__student')
        arrears_list = []
        for record in unpaid_records:
            record.calculate_late_fee()
            is_overdue = record.due_date < today
            arrears_list.append({
                'id': record.id,
                'student_id': record.plan.student_id,
                'student_name': record.plan.student.name,
                'student_phone': record.plan.student.phone,
                'plan_id': record.plan_id,
                'period': record.period,
                'amount': float(record.amount),
                'late_fee': float(record.late_fee),
                'total_due': float(record.amount) + float(record.late_fee),
                'due_date': record.due_date.isoformat(),
                'is_overdue': is_overdue,
                'status': 'overdue' if is_overdue else record.status,
                'late_fee_days': record.late_fee_days
            })
        return Response(arrears_list)


class FinancialStatsViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminOrFinance]

    @action(methods=['get'], detail=False)
    def revenue_by_package(self, request):
        from apps.packages.models import Package
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        payments_qs = Payment.objects.filter(status='confirmed')
        if start_date:
            payments_qs = payments_qs.filter(paid_at__date__gte=start_date)
        if end_date:
            payments_qs = payments_qs.filter(paid_at__date__lte=end_date)
        packages = Package.objects.all()
        result = []
        for pkg in packages:
            pkg_payments = payments_qs.filter(package=pkg)
            total_revenue = pkg_payments.aggregate(Sum('amount'))['amount__sum'] or 0
            student_count = pkg_payments.values('student').distinct().count()
            result.append({
                'package_id': pkg.id,
                'package_name': pkg.name,
                'package_type': pkg.type,
                'package_type_display': pkg.get_type_display(),
                'license_type': pkg.license_type,
                'total_revenue': float(total_revenue),
                'student_count': student_count,
                'base_price': float(pkg.base_price)
            })
        return Response(result)

    @action(methods=['get'], detail=False)
    def installment_revenue(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        payments_qs = Payment.objects.filter(
            status='confirmed',
            payment_type__in=['installment', 'down']
        )
        if start_date:
            payments_qs = payments_qs.filter(paid_at__date__gte=start_date)
        if end_date:
            payments_qs = payments_qs.filter(paid_at__date__lte=end_date)
        total_installment_revenue = payments_qs.aggregate(Sum('amount'))['amount__sum'] or 0
        down_payments = payments_qs.filter(payment_type='down')
        total_down = down_payments.aggregate(Sum('amount'))['amount__sum'] or 0
        total_installment_paid = payments_qs.filter(payment_type='installment').aggregate(Sum('amount'))['amount__sum'] or 0
        total_late_fee = InstallmentRecord.objects.filter(status='paid').aggregate(Sum('late_fee'))['late_fee__sum'] or 0
        total_plans = InstallmentPlan.objects.count()
        active_plans = InstallmentPlan.objects.filter(status__in=['unpaid', 'overdue']).count()
        paid_plans = InstallmentPlan.objects.filter(status='paid').count()
        total_remaining = InstallmentPlan.objects.filter(status__in=['unpaid', 'overdue']).aggregate(Sum('remaining_amount'))['remaining_amount__sum'] or 0
        return Response({
            'total_installment_revenue': float(total_installment_revenue),
            'total_down_payments': float(total_down),
            'total_installment_paid': float(total_installment_paid),
            'total_late_fee': float(total_late_fee),
            'total_plans': total_plans,
            'active_plans': active_plans,
            'paid_plans': paid_plans,
            'total_remaining': float(total_remaining)
        })

    @action(methods=['get'], detail=False)
    def exam_fee_revenue(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        payments_qs = Payment.objects.filter(
            status='confirmed',
            payment_type='makeup_exam'
        )
        if start_date:
            payments_qs = payments_qs.filter(paid_at__date__gte=start_date)
        if end_date:
            payments_qs = payments_qs.filter(paid_at__date__lte=end_date)
        total_exam_fee = payments_qs.aggregate(Sum('amount'))['amount__sum'] or 0
        exam_fees = ExamFee.objects.filter(status='paid')
        if start_date:
            exam_fees = exam_fees.filter(paid_at__date__gte=start_date)
        if end_date:
            exam_fees = exam_fees.filter(paid_at__date__lte=end_date)
        by_subject = exam_fees.values('subject').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('subject')
        subject_map = {1: '科目一', 2: '科目二', 3: '科目三', 4: '科目四'}
        subject_stats = []
        for item in by_subject:
            subject_stats.append({
                'subject': item['subject'],
                'subject_name': subject_map.get(item['subject'], '未知'),
                'count': item['count'],
                'total': float(item['total'] or 0)
            })
        return Response({
            'total_exam_fee': float(total_exam_fee),
            'by_subject': subject_stats,
            'unpaid_count': ExamFee.objects.filter(status='unpaid').count()
        })

    @action(methods=['get'], detail=False)
    def course_renewal_revenue(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        payments_qs = Payment.objects.filter(
            status='confirmed',
            payment_type='course_renewal'
        )
        if start_date:
            payments_qs = payments_qs.filter(paid_at__date__gte=start_date)
        if end_date:
            payments_qs = payments_qs.filter(paid_at__date__lte=end_date)
        total_renewal = payments_qs.aggregate(Sum('amount'))['amount__sum'] or 0
        renewal_count = payments_qs.count()
        return Response({
            'total_renewal_revenue': float(total_renewal),
            'renewal_count': renewal_count
        })

    @action(methods=['get'], detail=False)
    def summary(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        payments_qs = Payment.objects.filter(status='confirmed')
        if start_date:
            payments_qs = payments_qs.filter(paid_at__date__gte=start_date)
        if end_date:
            payments_qs = payments_qs.filter(paid_at__date__lte=end_date)
        total_revenue = payments_qs.aggregate(Sum('amount'))['amount__sum'] or 0
        by_type = payments_qs.values('payment_type').annotate(
            total=Sum('amount'),
            count=Count('id')
        )
        type_map = {
            'full': '一次性全款',
            'down': '首付',
            'installment': '分期还款',
            'makeup_exam': '补考费',
            'course_renewal': '续课费'
        }
        type_stats = []
        for item in by_type:
            type_stats.append({
                'payment_type': item['payment_type'],
                'payment_type_name': type_map.get(item['payment_type'], item['payment_type']),
                'total': float(item['total'] or 0),
                'count': item['count']
            })
        return Response({
            'total_revenue': float(total_revenue),
            'payment_count': payments_qs.count(),
            'by_payment_type': type_stats
        })

    @action(methods=['get'], detail=False)
    def monthly_trend(self, request):
        from django.db.models.functions import TruncMonth
        months = int(request.query_params.get('months', 6))
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)
        monthly_data = Payment.objects.filter(
            status='confirmed',
            paid_at__date__gte=start_date
        ).annotate(
            month=TruncMonth('paid_at')
        ).values('month').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('month')
        result = []
        for item in monthly_data:
            result.append({
                'month': item['month'].strftime('%Y-%m'),
                'total': float(item['total'] or 0),
                'count': item['count']
            })
        return Response(result)
