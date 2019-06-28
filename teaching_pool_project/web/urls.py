from django.urls import path, re_path

from . import views

app_name = 'web'

urlpatterns = [
    path('', views.index, name="index"),
    re_path(r'courses/(?P<year>\d{4}-\d{4})$', views.courses_full_list, name="courses_full_list"),
    re_path(r'courses/(?P<year>\d{4}-\d{4})/my', views.courses_list_year_teacher, name="courses_list_year_teacher"),
    re_path(r'TAs/request/(?P<course_id>\d*$)', views.request_for_TA, name="request_for_TA"),
    path('requests/TAs/', views.get_TAs_requests_to_validate, name="get_TAs_requests_to_validate"),
    re_path(r'requests/TAs/review/(?P<request_id>\d*$)', views.validate_request_for_TA, name="validate_request_for_TA"),
    re_path(r'requests/TAs/view/(?P<request_id>\d*$)', views.view_request_for_TA, name="view_request_for_TA"),
    path('requests/TAs/my/', views.requests_for_tas_teacher, name="requests_for_tas_teacher"),
    re_path(r'requests/TAs/my/(?P<status>.*$)', views.requests_for_tas_teacher_status, name="requests_for_tas_teacher_status"),
    path('profile/', views.update_my_profile, name="update_my_profile"),
    re_path('apply/(?P<course_id>\d*)', views.apply, name="apply"),
    path('applications/my/', views.my_applications, name='my_applications'),
    path('applications/', views.get_applications_for_my_courses, name='applications_for_my_courses'),
    re_path('applications/review/(?P<application_id>\d*)', views.review_application, name='review_application'),
]
