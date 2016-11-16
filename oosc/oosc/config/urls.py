
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
from oosc.attendance.views import ListCreateAttendance
from oosc.schools.views import ListCreateSchool
from oosc.constituencies.views import ListCreateCounstituency
from oosc.counties.views import ListCreateCounty
from oosc.classes.views import ListCreateClass
from oosc.teachers.views import ListCreateTeachers
from oosc.students.views import ListCreateStudent
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/attendance',ListCreateAttendance.as_view(),name="attendance-list-create"),
    url(r'^api/school',ListCreateSchool.as_view(),name="school-list-create"),
    url(r'^api/counties',ListCreateCounty.as_view(),name="county-list-create"),
    url(r'^api/counstituencies',ListCreateCounstituency.as_view(),name="counstituency-list-create"),
    url(r'^api/classes',ListCreateClass.as_view(),name="class-list-create"),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^api/students',ListCreateStudent.as_view(),name="list-create-student"),
    url(r'^api/teachers',ListCreateTeachers.as_view(),name="List-create-teachers")
]
