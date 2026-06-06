from django.db import models
from apps.students.models import Student
from apps.users.models import User
from apps.payments.models import Payment


class ExamFeeRule(models.Model):
    SUBJECT_CHOICES = (
        (1, '科目一（理论）'),
        (2, '科目二（场地）'),
        (3, '科目三（道路）'),
        (4, '科目四（安全文明）'),
    )

    subject = models.IntegerField(choices=SUBJECT_CHOICES, unique=True, verbose_name='考试科目')
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='补考费金额')
    description = models.TextField(blank=True, null=True, verbose_name='费用说明')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'exam_fee_rules'
        verbose_name = '补考费规则'
        verbose_name_plural = verbose_name
        ordering = ['subject']

    def __str__(self):
        return f'{self.get_subject_display()} - ¥{self.fee_amount}'


class ExamFee(models.Model):
    STATUS_CHOICES = (
        ('unpaid', '待缴费'),
        ('paid', '已缴费'),
        ('cancelled', '已取消'),
    )
    FEE_TYPE_CHOICES = (
        ('absent', '缺考'),
        ('failed', '考试未通过'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_fees', verbose_name='学员')
    subject = models.IntegerField(choices=ExamFeeRule.SUBJECT_CHOICES, verbose_name='考试科目')
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES, verbose_name='费用类型')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='费用金额')
    exam_booking = models.ForeignKey('ExamBooking', on_delete=models.CASCADE, related_name='exam_fees', verbose_name='关联约考记录', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid', verbose_name='状态')
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='exam_fee', verbose_name='关联缴费')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='缴费时间')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='exam_fees', verbose_name='经办人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'exam_fees'
        verbose_name = '补考账单'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return f'{self.student.name} - {self.get_subject_display()} - ¥{self.amount}'


class ExamRoom(models.Model):
    name = models.CharField(max_length=100, verbose_name='考场名称')
    address = models.CharField(max_length=200, verbose_name='考场地址')
    capacity = models.IntegerField(default=50, verbose_name='容纳人数')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'exam_rooms'
        verbose_name = '考场'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.name


class ExamSchedule(models.Model):
    SUBJECT_CHOICES = (
        (1, '科目一（理论）'),
        (2, '科目二（场地）'),
        (3, '科目三（道路）'),
        (4, '科目四（安全文明）'),
    )
    STATUS_CHOICES = (
        ('open', '预约开放'),
        ('locked', '预约关闭'),
        ('completed', '考试完成'),
        ('cancelled', '已取消'),
    )

    subject = models.IntegerField(choices=SUBJECT_CHOICES, verbose_name='考试科目')
    exam_room = models.ForeignKey(ExamRoom, on_delete=models.CASCADE, related_name='schedules', verbose_name='考场')
    exam_date = models.DateField(verbose_name='考试日期')
    start_time = models.TimeField(verbose_name='开始时间')
    end_time = models.TimeField(verbose_name='结束时间')
    total_quota = models.IntegerField(default=50, verbose_name='总名额')
    booked_quota = models.IntegerField(default=0, verbose_name='已预约')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name='状态')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'exam_schedules'
        verbose_name = '考试安排'
        verbose_name_plural = verbose_name
        ordering = ['-exam_date', '-start_time']

    @property
    def remaining_quota(self):
        return max(0, self.total_quota - self.booked_quota)

    def __str__(self):
        return f'{self.get_subject_display()} - {self.exam_room.name} - {self.exam_date}'


class ExamBooking(models.Model):
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '已约考'),
        ('absent', '缺考'),
        ('passed', '考试通过'),
        ('failed', '考试未通过'),
        ('cancelled', '已取消'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_bookings', verbose_name='学员')
    schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name='bookings', verbose_name='考试安排')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    booking_type = models.CharField(max_length=20, choices=(('admin', '管理员代约'), ('self', '自主约考')), default='admin', verbose_name='预约类型')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='exam_bookings', verbose_name='操作人')
    score = models.IntegerField(null=True, blank=True, verbose_name='考试分数')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    booked_at = models.DateTimeField(auto_now_add=True, verbose_name='预约时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'exam_bookings'
        verbose_name = '约考记录'
        verbose_name_plural = verbose_name
        ordering = ['-booked_at']
        unique_together = ['student', 'schedule']

    def __str__(self):
        return f'{self.student.name} - {self.schedule.get_subject_display()} - {self.get_status_display()}'
