from django.contrib import admin

# Register your models here.
from oosc.absence.models import Absence
class AdminClass(admin.ModelAdmin):
    list_display = ['id','student','status',"_class",'date_from','date_to']

admin.site.register(Absence,AdminClass)