from django.contrib import admin
from oosc.partner.models import Partner
# Register your models here.

class AdminClass(admin.ModelAdmin):
    list_display = ['id','name','user']

admin.site.register(Partner,AdminClass)
