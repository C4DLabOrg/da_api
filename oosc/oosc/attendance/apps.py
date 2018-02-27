import django
from django.apps import AppConfig


print ("Signals loaded....")
attendance_taken = django.dispatch.Signal(providing_args=["date", "present","absent","_class"])

class AttendanceConfig(AppConfig):
    name = 'oosc.attendance'
