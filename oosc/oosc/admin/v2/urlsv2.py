from django.conf.urls import url

from oosc.admin.v2.views import RestPassword, DeleteStreams

urlpatterns = [
    url(r'^reset-password', RestPassword.as_view(),name="reset_password"),
    url(r'^delete-schools-data', DeleteStreams.as_view(),name="reset_password"),
]