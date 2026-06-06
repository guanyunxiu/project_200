from django.db import models
from apps.users.models import User
from apps.packages.models import Package


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

    def __str__(self):
        return f'{self.name} - {self.get_license_type_display()}'
