from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *

app_name = 'api'

urlpatterns = {
    url(r'v1/persons/$', PersonCreateView.as_view(), name="persons"),
    url(r'v1/persons/?(?P<pk>[^/]+)/$', PersonDetail.as_view(), name="person_details")
}

urlpatterns = format_suffix_patterns(urlpatterns)
