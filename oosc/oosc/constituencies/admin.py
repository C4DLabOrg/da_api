from django.contrib import admin
from oosc.constituencies.models import Constituencies
# Register your models here.

class classAdmin(admin.ModelAdmin):
    list_display=['constituency','county_id']

admin.site.register(Constituencies,classAdmin);
