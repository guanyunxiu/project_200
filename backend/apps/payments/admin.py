from django.contrib import admin
from .models import Payment, InstallmentPlan, InstallmentRecord

admin.site.register(Payment)
admin.site.register(InstallmentPlan)
admin.site.register(InstallmentRecord)
