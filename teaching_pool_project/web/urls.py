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
    path('requests/TAs/reports/full_list/', views.courses_report, name="courses_report"),
    path('requests/TAs/reports/full_list/download/', views.download_course_report, name="download_course_report"),
    path('profile/', views.update_my_profile, name="update_my_profile"),
    path('profiles/', views.phds_profiles, name='phds_profiles'),
    re_path(r'profile/(?P<person_id>\d*)$', views.view_profile, name="view_profile"),
    re_path('apply/(?P<course_id>\d*)', views.apply, name="apply"),
    path('applications/my/', views.my_applications, name='my_applications'),
    re_path('applications/my/withdraw/(?P<application_id>\d*)', views.withdraw_application, name='withdraw_application'),
    path('applications/', views.get_applications_for_my_courses, name='applications_for_my_courses'),
    re_path('applications/review/(?P<application_id>\d*)', views.review_application, name='review_application'),
    path('config/', views.edit_config, name="edit_config"),
    path('config/add_phd', views.add_phd, name="add_phd"),
    path('reports/phds', views.phds_report, name="phds_report"),
    path('reports/applications', views.applications_list, name="applications_list"),
    re_path('applications/delete/(?P<application_id>\d*)', views.delete_application, name="delete_application"),
    path('reports/phds/download', views.download_phds_report, name="download_phds_report"),
    path('reports/phds/multiple_hirings', views.phds_with_multiple_hirings_report, name='phds_with_multiple_hirings_report'),
    path('api/search/phds', views.autocomplete_phds, name="autocomplete_phds"),
    path('api/search/phds_in_app', views.autocomplete_phds_from_person, name="autocomplete_phds_from_person"),
    path('api/search/courses', views.autocomplete_courses, name="autocomplete_courses"),
    path('api/applications/get_details', views.get_course_applications_details, name="api_get_course_applications_details"),
    path('assignments/add', views.add_assignment, name="add_assignment"),
]
