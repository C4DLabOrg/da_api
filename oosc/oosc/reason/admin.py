from django.contrib import admin

# Register your models here.
from oosc.reason.models import Reason
class AdminClass(admin.ModelAdmin):
    list_display = ['id','name']
admin.site.register(Reason,AdminClass)