from django.contrib import admin
from .models import Payment, InstallmentPlan, InstallmentRecord, InstallmentScheme, PaymentReminder

admin.site.register(Payment)
admin.site.register(InstallmentPlan)
admin.site.register(InstallmentRecord)
admin.site.register(InstallmentScheme)
admin.site.register(PaymentReminder)
