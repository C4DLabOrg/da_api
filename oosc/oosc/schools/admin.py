from django.contrib import admin
from oosc.schools.models import Schools
# Register your models here.

class classAdmin(admin.ModelAdmin):
    list_display=['id','school_code', 'school_name','level','status', 'latitude','longitude', 'emis_code', 'zone', 'source_of_water','headteacher'
        ,'phone_no']

admin.site.register(Schools,classAdmin);
