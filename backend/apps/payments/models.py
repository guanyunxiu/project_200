from django.db import models
from apps.students.models import Student
from apps.packages.models import Package
from apps.users.models import User


class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = (
        ('full', '一次性全款'),
        ('down', '首付'),
        ('installment', '分期还款'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('cash', '现金'),
        ('wechat', '微信'),
        ('alipay', '支付宝'),
        ('bank', '银行转账'),
        ('card', '刷卡'),
    )
    STATUS_CHOICES = (
        ('pending', '待确认'),
        ('confirmed', '已确认'),
        ('cancelled', '已取消'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments', verbose_name='学员')
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, related_name='payments', verbose_name='套餐')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, verbose_name='缴费类型')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name='支付方式')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='缴费金额')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='应缴总金额')
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='剩余未缴')
    installment_no = models.IntegerField(default=0, verbose_name='分期期次')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed', verbose_name='状态')
    receipt_no = models.CharField(max_length=50, unique=True, verbose_name='缴费凭证号')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='payments', verbose_name='经办人')
    paid_at = models.DateTimeField(auto_now_add=True, verbose_name='缴费时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'payments'
        verbose_name = '缴费记录'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return f'{self.student.name} - ¥{self.amount} - {self.get_payment_type_display()}'


class InstallmentPlan(models.Model):
    STATUS_CHOICES = (
        ('unpaid', '未还款'),
        ('paid', '已还款'),
        ('overdue', '已逾期'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='installments', verbose_name='学员')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='分期总金额')
    down_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='首付金额')
    months = models.IntegerField(verbose_name='分期期数')
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='每期金额')
    start_date = models.DateField(verbose_name='开始日期')
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='已还金额')
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='剩余金额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'installment_plans'
        verbose_name = '分期计划'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return f'{self.student.name} - {self.months}期 - ¥{self.monthly_amount}/期'


class InstallmentRecord(models.Model):
    plan = models.ForeignKey(InstallmentPlan, on_delete=models.CASCADE, related_name='records', verbose_name='分期计划')
    period = models.IntegerField(verbose_name='期次')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='还款金额')
    due_date = models.DateField(verbose_name='到期日')
    paid_date = models.DateField(null=True, blank=True, verbose_name='实际还款日期')
    status = models.CharField(max_length=20, choices=InstallmentPlan.STATUS_CHOICES, default='unpaid', verbose_name='状态')
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='installment_record', verbose_name='关联缴费')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'installment_records'
        verbose_name = '分期还款记录'
        verbose_name_plural = verbose_name
        ordering = ['plan', 'period']
