from django.contrib import admin
from oosc.classes.models import Classes
# Register your models here.

class classAdmin(admin.ModelAdmin):
    list_display=['id','class_name','school','teacher_id']

admin.site.register(Classes,classAdmin);
