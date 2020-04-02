from django.urls import path, re_path

from web.views import views, timereporting_views

app_name = 'web'

urlpatterns = [
    path('', views.index, name="index"),
    re_path(r'courses/(?P<year>\d{4}-\d{4})$', views.courses_full_list, name="courses_full_list"),
    re_path(r'courses/(?P<year>\d{4}-\d{4})/my', views.courses_list_year_teacher, name="courses_list_year_teacher"),
    re_path(r'TAs/request/(?P<course_id>\d*$)', views.request_for_TA, name="request_for_TA"),
    re_path(r'TAs/accept/(?P<course_id>\d*$)', views.accept_theoretical_number_of_tas, name="accept_theoretical_number_of_tas"),
    path('requests/TAs/', views.get_TAs_requests_to_validate, name="get_TAs_requests_to_validate"),
    re_path(r'requests/TAs/review/(?P<request_id>\d*$)', views.validate_request_for_TA, name="validate_request_for_TA"),
    re_path(r'requests/TAs/view/(?P<request_id>\d*$)', views.view_request_for_TA, name="view_request_for_TA"),
    path('requests/TAs/my/', views.requests_for_tas_teacher, name="requests_for_tas_teacher"),
    re_path(r'requests/TAs/my/(?P<status>.*$)', views.requests_for_tas_teacher_status, name="requests_for_tas_teacher_status"),
    re_path(r'requests/TAs/reports/full_list/(?P<year>\d{4}-\d{4})/(?P<term>.*)$', views.courses_report, name="courses_report"),
    re_path(r'requests/TAs/reports/full_list/(?P<year>\d{4}-\d{4})/(?P<term>.*)/download/$', views.download_course_report, name="download_course_report"),
    path('requests/TAs/reports/courses_without_requests/', views.get_courses_without_numberOfTARequests, name="get_courses_without_numberOfTARequests"),
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
    re_path('reports/phds/(?P<year>\d{4}-\d{4})/(?P<term>(HIVER|ETE))', views.phds_report, name="phds_report"),
    path('reports/applications', views.applications_list, name="applications_list"),
    re_path('applications/delete/(?P<application_id>\d*)', views.delete_application, name="delete_application"),
    re_path('reports/phds/download/(?P<year>\d{4}-\d{4})/(?P<term>(HIVER|ETE))', views.download_phds_report, name="download_phds_report"),
    path('reports/phds/multiple_hirings', views.phds_with_multiple_hirings_report, name='phds_with_multiple_hirings_report'),
    path('api/search/phds', views.autocomplete_phds, name="autocomplete_phds"),
    path('api/search/phds_in_app', views.autocomplete_phds_from_person, name="autocomplete_phds_from_person"),
    path('api/search/courses', views.autocomplete_courses, name="autocomplete_courses"),
    path('api/applications/get_details', views.get_course_applications_details, name="api_get_course_applications_details"),
    path('api/timereporting', timereporting_views.get_user_time_reports_api, name="get_user_time_reports_api"),
    re_path(r'api/timereporting/(?P<year>\d{4}-\d{4})/(?P<term>(winter|summer))$', timereporting_views.get_time_reports_api, name="get_time_reports_api"),
    path('api/timereporting/my', timereporting_views.get_user_time_reports, name="get_user_time_reports"),
    re_path(r'api/timereporting/teacher/(?P<id>\d*)', timereporting_views.get_teacher, name="get_teacher"),
    re_path(r'api/timereporting/course/(?P<id>\d*)', timereporting_views.get_course, name="get_course"),
    path('assignments/add', views.add_assignment, name="add_assignment"),
    path('timereporting/', timereporting_views.get_user_time_reports, name="get_user_time_reports"),
    path('timereporting/reports/', timereporting_views.reports_entry_page, name="reports_entry_page"),
    path('api/timereporting/reports/years/', timereporting_views.get_reports_years, name="get_reports_years"),
    path('api/timereporting/reports/terms/', timereporting_views.get_reports_terms, name='get_reports_terms'),
    re_path(r'timereporting/reports/(?P<year>\d{4}-\d{4})/(?P<term>(winter|summer))$', timereporting_views.get_time_reports, name="get_all_time_reports"),
    re_path(r'timereporting/reports/(?P<year>\d{4}-\d{4})/(?P<term>(winter|summer))/charts$', timereporting_views.reports_charts, name="reports_charts"),
    re_path(r'api/timereporting/reports/(?P<year>\d{4}-\d{4})/(?P<term>(winter|summer))/charts/chart_1', timereporting_views.get_data_for_report_chart_1, name="get_data_for_report_chart_1"),
    path('timereporting/add', timereporting_views.add_time_report, name="add_time_report"),
    re_path(r'timereporting/delete/(?P<id>\d*)', timereporting_views.delete_time_report, name="delete_time_report"),
    re_path(r'timereporting/edit/(?P<id>\d*)', timereporting_views.edit_time_report, name="edit_time_report"),
    path('api/search/my_courses', timereporting_views.autocomplete_my_courses, name="autocomplete_my_courses"),
    path('api/search/teachers', timereporting_views.autocomplete_all_teachers, name='autocomplete_all_teachers'),
    path('api/search/students', timereporting_views.autocomplete_all_students, name="autocomplete_all_students"),
    path('api/search/units', timereporting_views.autocomplete_all_units, name="autocomplete_all_units"),
]
