from django.contrib import admin
from .models import ExamRoom, ExamSchedule, ExamBooking, ExamFeeRule, ExamFee

admin.site.register(ExamRoom)
admin.site.register(ExamSchedule)
admin.site.register(ExamBooking)
admin.site.register(ExamFeeRule)
admin.site.register(ExamFee)
