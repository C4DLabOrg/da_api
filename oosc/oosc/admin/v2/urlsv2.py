from django.conf.urls import url

from oosc.admin.v2.views import RestPassword, DeleteStreams, RetrieveDeleteStream

urlpatterns = [
    url(r'^reset-password', RestPassword.as_view(),name="reset_password"),
    url(r'^delete-schools-data', DeleteStreams.as_view(),name="reset_password"),
    url(r'^teachers/(?P<pk>[0-9]+)/reset', RetrieveDeleteStream.as_view(),name="reset_password"),
]