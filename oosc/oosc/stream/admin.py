from django.contrib import admin
from oosc.stream.models import Stream
# Register your models here.

class classAdmin(admin.ModelAdmin):
    list_display=['id','_class','class_name','school']

admin.site.register(Stream, classAdmin);
