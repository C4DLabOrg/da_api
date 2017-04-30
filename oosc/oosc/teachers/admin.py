from django.contrib import admin
from oosc.teachers.models import Teachers
# Register your models here.
class classAdmin(admin.ModelAdmin):
    list_display=['user','fstname','lstname','active','phone_no','teacher_type','birthday','tsc_no','bom_no','qualifications','school_id','date_started_teaching','joined_current_school']

admin.site.register(Teachers,classAdmin);

