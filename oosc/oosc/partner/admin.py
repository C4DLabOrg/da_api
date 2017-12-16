from django.contrib import admin
from oosc.partner.models import Partner, PartnerAdmin


# Register your models here.

class AdminClass(admin.ModelAdmin):
    list_display = ['id','name','user','phone','test','last_data_upload']

admin.site.register(Partner,AdminClass)


class AdminClass1(admin.ModelAdmin):
    list_display = ['id','name','user','phone','test']

admin.site.register(PartnerAdmin,AdminClass1)

