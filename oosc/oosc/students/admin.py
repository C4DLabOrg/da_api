from django.contrib import admin
from oosc.students.models import Students
# Register your models here.

class classAdmin(admin.ModelAdmin):
    list_display=['id','emis_code','fstname','lstname','active','is_oosc','created','modified','date_enrolled','midname','total_absents','last_attendance','date_of_birth','admission_no','class_id','gender','previous_class','mode_of_transport','time_to_school','stay_with','household','meals_per_day','not_in_school_before','emis_code_histories','total_attendance']

admin.site.register(Students,classAdmin)
