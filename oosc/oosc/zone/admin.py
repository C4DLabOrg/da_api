from django.contrib import admin
from oosc.zone.models import Zone
# Register your models here.

class AdminClass(admin.ModelAdmin):
    list_display = ['id','county','subcounty','name']

admin.site.register(Zone,AdminClass)

