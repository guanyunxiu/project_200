from django.contrib import admin
from .models import ExamRoom, ExamSchedule, ExamBooking

admin.site.register(ExamRoom)
admin.site.register(ExamSchedule)
admin.site.register(ExamBooking)
