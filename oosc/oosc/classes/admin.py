from django.contrib import admin
from oosc.classes.models import Classes
# Register your models here.

class classAdmin(admin.ModelAdmin):
    list_display=['name','created','modified']

admin.site.register(Classes,classAdmin);
