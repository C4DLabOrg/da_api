from django.conf.urls import url

from oosc.attendance.v2.views import ExportMonthlyAttendances, MonitorAttendanceTaking

urlpatterns = [
    url(r'^export/?', ExportMonthlyAttendances.as_view(),name="reset_password"),
    url(r'^monitor/?', MonitorAttendanceTaking.as_view(),name="reset_password"),
]