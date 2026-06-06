from django.db import models


class Package(models.Model):
    TYPE_CHOICES = (
        ('normal', '普通班'),
        ('premium', '精品班'),
        ('vip', 'VIP班'),
    )
    LICENSE_TYPE_CHOICES = (
        ('C1', 'C1证'),
        ('C2', 'C2证'),
        ('D', 'D证'),
        ('all', '通用'),
    )
    PAYMENT_TYPE_CHOICES = (
        ('full', '一次性付款'),
        ('installment', '分期付款'),
        ('both', '支持两种'),
    )

    name = models.CharField(max_length=100, verbose_name='套餐名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='套餐编码')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='套餐类型')
    license_type = models.CharField(max_length=10, choices=LICENSE_TYPE_CHOICES, default='all', verbose_name='适用驾照类型')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='基准报名费')
    total_hours = models.IntegerField(default=0, verbose_name='包含课时')
    description = models.TextField(blank=True, null=True, verbose_name='套餐描述')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='both', verbose_name='付款方式')
    down_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='分期首付')
    installment_months = models.IntegerField(default=0, verbose_name='分期期数')
    installment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='每期金额')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'packages'
        verbose_name = '报名套餐'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return f'{self.name} - ¥{self.base_price}'
