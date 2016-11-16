from django.contrib import admin
from oosc.subjects.models import Subjects
# Register your models here.
class classAdmin(admin.ModelAdmin):
    list_display=['subject_name','id']

admin.site.register(Subjects,classAdmin);

