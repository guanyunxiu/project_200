from django.db import models
from django.db.models import Sum
from apps.students.models import Student
from apps.packages.models import Package
from apps.users.models import User
from datetime import date


class InstallmentScheme(models.Model):
    name = models.CharField(max_length=100, verbose_name='方案名称')
    down_payment_ratio = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='首付比例(%)', help_text='如30表示首付30%')
    periods = models.IntegerField(verbose_name='分期期数', help_text='如6表示分6期')
    due_day = models.IntegerField(verbose_name='每期还款日', help_text='如15表示每月15日还款')
    late_fee_ratio = models.DecimalField(max_digits=5, decimal_places=4, verbose_name='逾期滞纳金比例(%)', help_text='每日滞纳金比例，如0.05表示每日0.05%')
    description = models.TextField(blank=True, null=True, verbose_name='方案描述')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'installment_schemes'
        verbose_name = '分期方案'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return f'{self.name} - 首付{self.down_payment_ratio}% - {self.periods}期'


class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = (
        ('full', '一次性全款'),
        ('down', '首付'),
        ('installment', '分期还款'),
        ('makeup_exam', '补考费'),
        ('course_renewal', '续课费'),
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
    scheme = models.ForeignKey(InstallmentScheme, on_delete=models.SET_NULL, null=True, blank=True, related_name='plans', verbose_name='分期方案')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='分期总金额')
    down_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='首付金额')
    months = models.IntegerField(verbose_name='分期期数')
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='每期金额')
    start_date = models.DateField(verbose_name='开始日期')
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='已还金额')
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='剩余金额')
    total_late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='累计滞纳金')
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

    def update_overdue_status(self):
        today = date.today()
        overdue_records = self.records.filter(status='unpaid', due_date__lt=today)
        if overdue_records.exists():
            self.status = 'overdue'
            self.save()

    def calculate_total_late_fee(self):
        total = self.records.aggregate(Sum('late_fee'))['late_fee__sum'] or 0
        self.total_late_fee = total
        self.save()
        return total


class PaymentReminder(models.Model):
    REMINDER_TYPE_CHOICES = (
        ('phone', '电话'),
        ('sms', '短信'),
        ('wechat', '微信'),
        ('visit', '上门'),
        ('other', '其他'),
    )
    REMINDER_RESULT_CHOICES = (
        ('promised', '承诺还款'),
        ('partial', '部分还款'),
        ('no_answer', '无人接听'),
        ('refused', '拒绝还款'),
        ('pending', '待跟进'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payment_reminders', verbose_name='学员')
    installment_plan = models.ForeignKey(InstallmentPlan, on_delete=models.CASCADE, related_name='reminders', verbose_name='分期计划')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES, verbose_name='催缴方式')
    reminder_date = models.DateField(auto_now_add=True, verbose_name='催缴日期')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='催缴金额')
    result = models.CharField(max_length=20, choices=REMINDER_RESULT_CHOICES, verbose_name='催缴结果')
    promised_date = models.DateField(null=True, blank=True, verbose_name='承诺还款日期')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='payment_reminders', verbose_name='经办人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'payment_reminders'
        verbose_name = '催缴记录'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return f'{self.student.name} - {self.get_reminder_type_display()} - {self.reminder_date}'


class InstallmentRecord(models.Model):
    plan = models.ForeignKey(InstallmentPlan, on_delete=models.CASCADE, related_name='records', verbose_name='分期计划')
    period = models.IntegerField(verbose_name='期次')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='还款金额')
    due_date = models.DateField(verbose_name='到期日')
    paid_date = models.DateField(null=True, blank=True, verbose_name='实际还款日期')
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='滞纳金')
    late_fee_days = models.IntegerField(default=0, verbose_name='逾期天数')
    status = models.CharField(max_length=20, choices=InstallmentPlan.STATUS_CHOICES, default='unpaid', verbose_name='状态')
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='installment_record', verbose_name='关联缴费')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'installment_records'
        verbose_name = '分期还款记录'
        verbose_name_plural = verbose_name
        ordering = ['plan', 'period']

    def calculate_late_fee(self):
        if self.status == 'paid':
            return self.late_fee
        today = date.today()
        if today <= self.due_date:
            self.late_fee = 0
            self.late_fee_days = 0
            return 0
        days_overdue = (today - self.due_date).days
        self.late_fee_days = days_overdue
        late_fee_ratio = 0
        if self.plan.scheme:
            late_fee_ratio = float(self.plan.scheme.late_fee_ratio) / 100
        else:
            late_fee_ratio = 0.0005
        self.late_fee = round(float(self.amount) * late_fee_ratio * days_overdue, 2)
        self.save()
        self.plan.calculate_total_late_fee()
        return self.late_fee

    @property
    def total_amount_due(self):
        return float(self.amount) + float(self.late_fee)
