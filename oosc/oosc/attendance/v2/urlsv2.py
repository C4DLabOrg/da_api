from django.conf.urls import url

from oosc.attendance.v2.views import ExportMonthlyAttendances

urlpatterns = [
    url(r'^export', ExportMonthlyAttendances.as_view(),name="reset_password"),
]