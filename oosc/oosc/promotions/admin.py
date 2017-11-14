from django.contrib import admin

# Register your models here.
from oosc.promotions.models import PromoteSchool, PromoteStream


class AdminClass(admin.ModelAdmin):
    list_display = ['id','school','year','graduates_class','created','modified','completed']

admin.site.register(PromoteSchool,AdminClass)


class AdminClassStream(admin.ModelAdmin):
    list_display = [ 'id', 'prev_class','next_class','promote_school','created','modified','completed']

admin.site.register(PromoteStream,AdminClassStream)




