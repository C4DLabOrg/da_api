from django.contrib import admin
from oosc.history.models import History
# Register your models here.

class classAdmin(admin.ModelAdmin):
    list_display=['student','_class','joined','created','modified','joined_description','left','left_description']

admin.site.register(History,classAdmin);
