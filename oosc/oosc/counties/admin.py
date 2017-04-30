from django.contrib import admin
from oosc.counties.models import Counties
# Register your models here.

class classAdmin(admin.ModelAdmin):
    list_display=['county_name','id']

admin.site.register(Counties,classAdmin);
