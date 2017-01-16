from django.contrib import admin
from oosc.subcounty.models import SubCounty
# Register your models here.

class AdminClass(admin.ModelAdmin):
    list_display = ['id','county','name']

admin.site.register(SubCounty,AdminClass)

