from django.conf.urls import url

from oosc.admin.v2.views import RestPassword, DeleteStreams, RetrieveDeleteStream, DeleteStudentsByStreams, \
    ListDuplicatePartnerSchools

urlpatterns = [
    url(r'^reset-password', RestPassword.as_view(),name="reset_password"),
    url(r'^delete-schools-data', DeleteStreams.as_view(),name="reset_password"),
    url(r'^duplicate-partner-schools', ListDuplicatePartnerSchools.as_view(),name="duplicate_partner_schools"),
    url(r'^delete-streams', DeleteStudentsByStreams.as_view(),name="delete_streams_password"),
    url(r'^teachers/(?P<pk>\w{3,17})/reset', RetrieveDeleteStream.as_view(),name="reset_password"),
]