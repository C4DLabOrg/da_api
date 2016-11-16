from django.contrib import admin
from oosc.schools.models import Schools
# Register your models here.

class classAdmin(admin.ModelAdmin):
    list_display=['school_code', 'school_name', 'geo_cordinates', 'emis_code', 'constituency', 'source_of_water','headteacher'
        ,'phone_no']

admin.site.register(Schools,classAdmin);
