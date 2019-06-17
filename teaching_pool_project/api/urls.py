from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import *

app_name = 'api'

urlpatterns = {
    url(r'v1/persons/$', Persons.as_view(), name="persons"),
    url(r'v1/persons/?(?P<pk>[^/]+)/$', PersonDetail.as_view(), name="person_details"),
    url(r'v1/courses/$', Courses.as_view(), name="courses"),
    url(r'v1/courses/(?P<pk>\d*)/$', CourseDetail.as_view(), name="course_details_by_id"),
    url(r'v1/courses/(?P<year>.*)/(?P<term>.*)/(?P<code>.*)/$', CourseDetailByYearTermCode.as_view(), name="course_details_by_year_term_code"),
    url(r'v1/teachings/$', Teachings.as_view(), name="teachings"),
    url(r'v1/teachings/(?P<sciper>\d*)/$', TeachingsBySciper.as_view(), name="teachings_by_sciper")
}

urlpatterns = format_suffix_patterns(urlpatterns)
