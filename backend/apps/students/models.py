from django.db import models
from apps.users.models import User
from apps.packages.models import Package
from datetime import date


class HourRecord(models.Model):
    HOUR_TYPE_CHOICES = (
        ('theory', '理论课时'),
        ('practical', '实操课时'),
    )
    OPERATION_TYPE_CHOICES = (
        ('consume', '核销'),
        ('add', '增加'),
        ('refund', '退还'),
        ('renewal', '续课'),
    )

    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='hour_records', verbose_name='学员')
    hour_type = models.CharField(max_length=20, choices=HOUR_TYPE_CHOICES, verbose_name='课时类型')
    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPE_CHOICES, verbose_name='操作类型')
    hours = models.IntegerField(verbose_name='课时数量')
    hours_before = models.IntegerField(verbose_name='操作前课时')
    hours_after = models.IntegerField(verbose_name='操作后课时')
    coach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'coach'}, related_name='hour_records', verbose_name='教练')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='hour_records_operator', verbose_name='操作人')
    sign_in_time = models.DateTimeField(null=True, blank=True, verbose_name='签到时间')
    sign_out_time = models.DateTimeField(null=True, blank=True, verbose_name='签退时间')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'hour_records'
        verbose_name = '课时核销记录'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return f'{self.student.name} - {self.get_hour_type_display()} - {self.get_operation_type_display()} {self.hours}课时'


class Student(models.Model):
    LICENSE_TYPE_CHOICES = (
        ('C1', 'C1证（手动挡）'),
        ('C2', 'C2证（自动挡）'),
        ('D', 'D证（摩托车）'),
    )
    STATUS_CHOICES = (
        ('studying', '学习中'),
        ('graduated', '已毕业'),
        ('suspended', '已休学'),
        ('cancelled', '已取消'),
    )
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='student', verbose_name='关联账号')
    name = models.CharField(max_length=50, verbose_name='姓名')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name='性别')
    phone = models.CharField(max_length=20, unique=True, verbose_name='手机号')
    id_card = models.CharField(max_length=18, unique=True, verbose_name='身份证号')
    license_type = models.CharField(max_length=10, choices=LICENSE_TYPE_CHOICES, verbose_name='驾照类型')
    birthday = models.DateField(verbose_name='出生日期')
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name='住址')
    id_card_front = models.ImageField(upload_to='students/id_cards/', blank=True, null=True, verbose_name='身份证正面')
    id_card_back = models.ImageField(upload_to='students/id_cards/', blank=True, null=True, verbose_name='身份证背面')
    photo = models.ImageField(upload_to='students/photos/', blank=True, null=True, verbose_name='学员照片')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='studying', verbose_name='状态')
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True, related_name='students', verbose_name='报名套餐')
    coach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'coach'}, related_name='coached_students', verbose_name='所属教练')
    total_hours = models.IntegerField(default=0, verbose_name='总课时')
    used_hours = models.IntegerField(default=0, verbose_name='已用课时')
    theory_hours = models.IntegerField(default=0, verbose_name='理论总课时')
    used_theory_hours = models.IntegerField(default=0, verbose_name='已用理论课时')
    practical_hours = models.IntegerField(default=0, verbose_name='实操总课时')
    used_practical_hours = models.IntegerField(default=0, verbose_name='已用实操课时')
    last_hours_reminder = models.DateTimeField(null=True, blank=True, verbose_name='上次课时提醒时间')
    enroll_date = models.DateField(auto_now_add=True, verbose_name='报名日期')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'students'
        verbose_name = '学员'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    @property
    def remaining_hours(self):
        return max(0, self.total_hours - self.used_hours)

    @property
    def remaining_theory_hours(self):
        return max(0, self.theory_hours - self.used_theory_hours)

    @property
    def remaining_practical_hours(self):
        return max(0, self.practical_hours - self.used_practical_hours)

    @property
    def hours_remaining_percent(self):
        if self.total_hours == 0:
            return 100
        return round((self.remaining_hours / self.total_hours) * 100, 1)

    @property
    def is_hours_low(self):
        return self.hours_remaining_percent <= 20 or self.remaining_hours <= 3

    @property
    def is_hours_depleted(self):
        return self.remaining_hours <= 0

    def need_hours_reminder(self):
        if not self.is_hours_low:
            return False
        from datetime import datetime, timedelta
        if self.last_hours_reminder:
            return (datetime.now() - self.last_hours_reminder.replace(tzinfo=None)) > timedelta(days=7)
        return True

    def __str__(self):
        return f'{self.name} - {self.get_license_type_display()}'
