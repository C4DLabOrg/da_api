from django.contrib import admin
from oosc.stream.models import Stream,GraduatesStream
# Register your models here.

class classAdmin(admin.ModelAdmin):
    list_display=['id','_class','class_name','school']

class classAdmin2(admin.ModelAdmin):
    list_display=['id','class_name','school','year']

admin.site.register(Stream, classAdmin)
admin.site.register(GraduatesStream, classAdmin2)