from django.contrib import admin
from  oosc.attendance.models import Attendance
class AttendaceAdmin(admin.ModelAdmin):
    list_display=['student_id','date','cause_of_absence','class_id']

admin.site.register(Attendance,AttendaceAdmin)
# Register your models here.
