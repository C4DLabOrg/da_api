
"""oosc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from oosc.attendance.views import ListCreateAttendance,TakeAttendance,WeeklyAttendanceReport
from oosc.schools.views import ListCreateSchool,ImportSchools
from oosc.constituencies.views import ListCreateCounstituency
from oosc.counties.views import ListCreateCounty
from oosc.classes.views import ListCreateClass
from oosc.teachers.views import ListCreateTeachers,ListTeachers
from oosc.students.views import ListCreateStudent
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from oosc.absence.views import GetEditAbsence
from oosc.reason.views import ListCreatereason
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/attendance/weekly',WeeklyAttendanceReport.as_view(),name="weekly_attendance_report"),
    url(r'^api/attendance',TakeAttendance.as_view(),name="take_attendance"),
    url(r'^api/absent/(?P<pk>[0-9]+)',GetEditAbsence.as_view(),name="Update_absent"),
    url(r'^api/reasons',ListCreatereason.as_view(),name="list_create_reason"),
    url(r'^api/attendances',ListCreateAttendance.as_view(),name="attendance-list-create"),
    url(r'^api/schools/import',ImportSchools.as_view(),name="import_schools"),
    url(r'^api/school',ListCreateSchool.as_view(),name="school-list-create"),
    url(r'^api/counties',ListCreateCounty.as_view(),name="county-list-create"),
    url(r'^api/zones',ListCreateCounstituency.as_view(),name="zones-list-create"),
    url(r'^api/classes',ListCreateClass.as_view(),name="class-list-create"),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^api/students',ListCreateStudent.as_view(),name="list-create-student"),
    url(r'^api/teacher$',ListCreateTeachers.as_view(),name="List-create-teachers"),
    url(r'^api/teachers',ListTeachers.as_view(),name="List_Teachers"),

]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
