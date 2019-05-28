from django.conf.urls import url

from oosc.attendance.v2.views import ExportMonthlyAttendances, MonitorAttendanceTaking, ImportAttendance, \
    ListCreateAttendanceHistory

urlpatterns = [
    url(r'^export/?', ExportMonthlyAttendances.as_view(),name="export_attendance"),
    url(r'^monitor/?', MonitorAttendanceTaking.as_view(),name="monitor_attendance"),
    url(r'^import/?', ImportAttendance.as_view(),name="import_attendance"),
    url(r'^histories/?', ListCreateAttendanceHistory.as_view(),name="attendance_history"),
]