# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from functools import wraps

import xlwt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Prefetch
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template import Context
from django.template.loader import get_template
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.views import generic

from epfl.sti.helpers import ldap as epfl_ldap
from web.helpers import config

from .forms import *
from .models import *

logger = logging.getLogger(__name__)

User = get_user_model()


def is_superuser():
    def has_superuser_profile(u):
        logger.debug("Checking if %s is superuser", u.username)
        if u.is_superuser:
            return True
        raise PermissionDenied
    return user_passes_test(has_superuser_profile)


def is_staff():
    def has_staff_profile(u):
        logger.debug("Checking if %s is staff", u.username)
        if u.is_staff:
            return True
        raise PermissionDenied
    return user_passes_test(has_staff_profile)


def is_staff_or_teacher():
    def has_staff_or_teacher_profile(u):
        if u.is_superuser:
            return True
        elif u.is_staff:
            return True
        elif u.groups.filter(name='teachers').exists():
            return True
        else:
            raise PermissionDenied
    return user_passes_test(has_staff_or_teacher_profile)


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""

    def in_groups(u):
        logger.debug("Checking if %s is member of the '%s' group(s)",
                     u.username, group_names)
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        raise PermissionDenied
    return user_passes_test(in_groups)


def index(request):
    year = config.get_config('current_year')

    if request.user.is_staff and NumberOfTAUpdateRequest.objects.filter(status="Pending").exists():
        messages.info(
            request, mark_safe("<i class='fas fa-info-circle'></i>&nbsp;You have (a) pending <a href='{}'>TA request(s) to validate</a>".format(reverse('web:get_TAs_requests_to_validate'))))

    if request.user.groups.filter(name='phds').exists() and not Availability.objects.filter(year=year, person=request.user).exists():
        message = mark_safe(
            "<i class='fas fa-info-circle'></i>&nbsp;You should <a href='{}'>update your profile</a>.".format(reverse('web:update_my_profile')))
        messages.info(request, message)
    return render(request, 'web/index.html')


def courses_full_list(request, year):
    year = config.get_config('current_year')
    term = config.get_config('current_term')

    all_courses = Course.objects.filter(
        year=year, term=term).prefetch_related('teachers').all()
    user_is_phd = request.user.groups.filter(name="phds").exists()
    if user_is_phd:
        courses_applied_to = [application.course.pk for application in Applications.objects.filter(
            applicant=request.user).all()]
    else:
        courses_applied_to = []

    messages.info(request, mark_safe("<i class='fas fa-sticky-note'></i>&nbsp;Study plans: <a href='https://edu.epfl.ch/studyplan/en/bachelor' target=^_blank'>bachelor</a>, <a href='https://edu.epfl.ch/studyplan/en/master' target='_blank'>master</a>"))
    context = {
        'year': year,
        'courses': all_courses,
        'user_is_phd': user_is_phd,
        'courses_applied_to': courses_applied_to,
    }
    return render(request, 'web/all_courses.html', context)


@group_required('teachers')
def courses_list_year_teacher(request, year):
    year = config.get_config('current_year')
    term = config.get_config('current_term')

    courses = Course.objects.filter(
        year=year, term=term, teachers=request.user).prefetch_related('teachers').all()

    context = {
        'courses': courses,
    }
    return render(request, 'web/prof_courses.html', context)


@group_required('teachers')
def get_applications_for_my_courses(request):
    teachings = Teaching.objects.filter(
        person=request.user).prefetch_related('course').all()
    courses_ids = [item.course.pk for item in teachings]
    applications = Applications.objects.filter(
        course_id__in=courses_ids).select_related('course').all()
    context = {
        'applications': applications,
    }
    return render(request, 'web/applications_to_my_courses.html', context)


@group_required('teachers')
def review_application(request, application_id):
    application = get_object_or_404(Applications, pk=application_id)
    application_form = ApplicationForm_teacher(
        request.POST or None, instance=application)

    if request.method == "POST":
        if 'Approve' in request.POST:
            status = "Hired"
        elif 'Reject' in request.POST:
            status = "Rejected"

        if application_form.is_valid():

            application_form.save(commit=False)
            application.status = status
            application.closedAt = now()
            application.closedBy = request.user
            if application_form.cleaned_data['decisionReason']:
                application.decisionReason = application_form.cleaned_data['decisionReason']
            application.save()
            messages.success(request, "Your decision has been recorded")
            return HttpResponseRedirect(reverse('web:applications_for_my_courses'))

    context = {
        'course': application.course,
        'person': application.applicant,
        'form': application_form,
        'application_id': application.pk,
    }

    return render(request, 'web/application_review_form.html', context)


@group_required('teachers')
def requests_for_tas_teacher(request):
    requests = NumberOfTAUpdateRequest.objects.filter(
        requester=request.user).prefetch_related('course').order_by('openedAt').all()
    context = {
        'requests': requests
    }
    return render(request, 'web/prof_ta_requests.html', context)


@group_required('teachers')
def requests_for_tas_teacher_status(request, status):
    requests = NumberOfTAUpdateRequest.objects.filter(
        requester=request.user, status=status.capitalize()).prefetch_related('course').order_by('openedAt').all()
    context = {
        'requests': requests
    }
    return render(request, 'web/prof_ta_requests.html', context)


@group_required('teachers')
def request_for_TA(request, course_id):
    if not config.get_config('requests_for_TAs_are_open'):
        messages.error(
            request, "The requests for Teaching Assistants are not open at the moment.")
        return render(request, 'web/blank.html')

    course = get_object_or_404(Course, pk=course_id)

    year = config.get_config('current_year')
    term = config.get_config('current_term')
    if course.year != year or course.term != term:
        messages.error(
            request, "The requests for Teaching Assistants are not open for this year / term")
        return render(request, 'web/blank.html')

    try:
        ta_request = NumberOfTAUpdateRequest.objects.get(
            status="Pending", course=course)
    except ObjectDoesNotExist:
        ta_request = NumberOfTAUpdateRequest()
        ta_request.course = course
        ta_request.requester = request.user
        ta_request.openedAt = now()
        ta_request.requestedNumberOfTAs = course.calculatedNumberOfTAs

    form = RequestForTA(request.POST or None, instance=ta_request)

    if request.method == "POST":
        if form.is_valid():
            ta_request.openedAt = now()
            ta_request.requestedNumberOfTAs = form.cleaned_data['requestedNumberOfTAs']
            ta_request.requestReason = form.cleaned_data['requestReason']
            ta_request.save_and_notify()
            messages.success(
                request, "Your request for TAs has been successfully saved")
            return HttpResponseRedirect(reverse('web:courses_list_year_teacher', args=[config.get_config('current_year')]))

    context = {
        'course_id': course_id,
        'course': course,
        'form': form
    }
    return render(request, 'web/request_for_ta_form.html', context)


@is_staff()
def get_TAs_requests_to_validate(request):
    requests = NumberOfTAUpdateRequest.objects.filter(status='Pending').all()
    sections = Section.objects.all()
    context = {
        'requests': requests,
        'sections': sections,
    }
    return render(request, 'web/requests_for_tas.html', context)


@is_staff()
def validate_request_for_TA(request, request_id):
    if request.method == 'POST':
        form = RequestForTAApproval(request.POST)
        if form.is_valid():
            if 'Approve' in request.POST:
                status = "Approved"
            elif 'Decline' in request.POST:
                status = "Declined"

            request_obj = NumberOfTAUpdateRequest.objects.get(
                pk=form.cleaned_data['request_id'])
            request_obj.status = status
            request_obj.decisionReason = form.cleaned_data['reason_for_decision']
            request_obj.closedAt = now()
            person = request.user
            request_obj.decidedBy = request.user
            request_obj.save_and_notify()

            return HttpResponseRedirect(reverse('web:get_TAs_requests_to_validate'))

    else:
        requestForTA = NumberOfTAUpdateRequest.objects.get(pk=request_id)
        form = RequestForTAApproval()
        form.fields['request_id'].initial = requestForTA.pk
        form.fields['opened_at'].initial = requestForTA.openedAt
        form.fields['requester'].initial = "{}, {}".format(
            requestForTA.requester.last_name, requestForTA.requester.first_name)
        form.fields['course'].initial = "{} ({})".format(
            requestForTA.course.subject, requestForTA.course.code)
        form.fields['requestedNumberOfTAs'].initial = requestForTA.requestedNumberOfTAs
        form.fields['reason_for_request'].initial = requestForTA.requestReason

        course = requestForTA.course
        context = {
            'request_id': request_id,
            'course': course,
            'form': form
        }
        return render(request, 'web/request_for_ta_review_form.html', context)


@group_required('teachers')
def view_request_for_TA(request, request_id):
    ta_request = get_object_or_404(NumberOfTAUpdateRequest, pk=request_id)
    form = RequestForTAView()
    form.fields['request_id'].initial = ta_request.pk
    form.fields['opened_at'].initial = ta_request.openedAt
    form.fields['requester'].initial = "{}, {}".format(
        ta_request.requester.last_name, ta_request.requester.first_name)
    form.fields['course'].initial = "{} ({})".format(
        ta_request.course.subject, ta_request.course.code)
    form.fields['requestedNumberOfTAs'].initial = ta_request.requestedNumberOfTAs
    form.fields['reason_for_request'].initial = ta_request.requestReason
    form.fields['status'].initial = ta_request.status
    form.fields['reason_for_decision'].initial = ta_request.decisionReason

    course = ta_request.course
    context = {
        'course': course,
        'request_id': request_id,
        'form': form
    }

    return render(request, 'web/request_for_ta_view_form.html', context)


@group_required('phds')
def apply(request, course_id):
    if not config.get_config('applications_are_open'):
        messages.error(
            request, "The applications for Teaching Assistants positions are not open at the moment.")
        return render(request, 'web/blank.html')

    course = get_object_or_404(Course, pk=course_id)

    year = config.get_config('current_year')
    term = config.get_config('current_term')
    if course.year != year or course.term != term:
        messages.error(
            request, "The applications for Teaching Assistants positions are not open for this year / term")
        return render(request, 'web/blank.html')

    try:
        application = Applications.objects.get(
            applicant=request.user, course=course)
    except ObjectDoesNotExist:
        application = Applications()
        application.course = course
        application.applicant = request.user

    application_form = ApplicationForm_phd(
        request.POST or None, instance=application)

    if request.method == "POST":
        if application_form.is_valid():
            application_form.save(commit=False)
            application.save()
            messages.success(request, "Your application has been submitted")
            return HttpResponseRedirect(reverse('web:courses_full_list', args=[course.year]))

    context = {
        'course': course,
        'form': application_form
    }

    return render(request, 'web/application_form.html', context)


@group_required('phds')
def update_my_profile(request):
    year = config.get_config('current_year')

    # Working with the availabilities
    availability, availability_created = Availability.objects.get_or_create(
        person=request.user, year=year)
    if availability_created:
        messages.warning(
            request, "Since you did not fill in your profile, your default availability has been set to 'Available'")
    availability_form = AvailabilityForm(
        request.POST or None, instance=availability)

    # Working with the languages
    languages_form = LanguagesForm(request.POST or None)
    if not request.POST:
        languages = list()
        if request.user.canTeachInFrench:
            languages.append("f")
        if request.user.canTeachInEnglish:
            languages.append("e")
        if request.user.canTeachInGerman:
            languages.append("g")
        languages_form = LanguagesForm(initial={'languages': languages})

    # Working with the topics
    topics_form = TopicForm(request.POST or None, instance=request.user)

    if request.method == "POST":
        complete_form_is_OK = True

        if availability_form.is_valid():
            availability_form.save(commit=False)
            availability.save()
        else:
            messages.error(
                request, "The availability section contains error. Please review it")
            complete_form_is_OK = False

        if languages_form.is_valid():
            request.user.canTeachInFrench = 'f' in languages_form.cleaned_data['languages']
            request.user.canTeachInEnglish = 'e' in languages_form.cleaned_data['languages']
            request.user.canTeachInGerman = 'g' in languages_form.cleaned_data['languages']
            request.user.save()
        else:
            messages.error(
                request, "The languages section contains error. Please review it")
            complete_form_is_OK = False

        # Topics
        if topics_form.is_valid():
            topics_form.save()

        else:
            messages.error(
                request, "The list of selected topics contains error(s). Please review it")
            complete_form_is_OK = False

        if complete_form_is_OK:
            messages.success(
                request, "Your profile has been succesfully updated.")

    context = {
        'year': year,
        'availability_form': availability_form,
        'languages_form': languages_form,
        'topics_form': topics_form,
    }
    return render(request, 'web/profile.html', context)


@group_required('phds')
def my_applications(request):
    applications = Applications.objects.filter(
        applicant=request.user).prefetch_related('course').all()
    context = {
        'applications': applications,
    }
    return render(request, 'web/applications.html', context)


@is_staff()
def edit_config(request):
    config = Config.objects.first()
    if not config:
        config = Config()

    config_form = ConfigForm(request.POST or None, instance=config)

    if request.method == "POST":
        if config_form.is_valid():
            config_form.save()
            messages.success(
                request, "The configuration has been successfully saved")

    context = {
        'config_form': config_form,
    }

    return render(request, 'web/config_form.html', context)


@is_staff()
def courses_report(request):
    year = config.get_config('current_year')
    term = config.get_config('current_term')

    courses = Course.objects.filter(
        year=year, term=term).prefetch_related('teachers').all()
    sections_dict = dict()
    sections_obj = Section.objects.values('id', 'name').all()
    for section in sections_obj:
        sections_dict[section['id']] = section['name']

    context = {
        'sections': sections_dict,
        'courses': courses
    }

    return render(request, 'web/reports/courses_list.html', context)


@is_staff()
def download_course_report(request):
    year = config.get_config('current_year')
    term = config.get_config('current_term')

    courses = Course.objects.filter(
        year=year, term=term).prefetch_related('teachers').all()

    # Get base data about sections in order NOT TO re-query the DB for each teacher of each courses
    sections_obj = Section.objects.values('id', 'name').all()
    sections_dict = dict()
    for section in sections_obj:
        sections_dict[section['id']] = section['name']

    # content-type of response
    response = HttpResponse(content_type='application/ms-excel')

    # decide file name
    response['Content-Disposition'] = 'attachment; filename="{year}_{term}.xls"'.format(
        year=year, term=term)

    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')

    # adding sheet
    ws = wb.add_sheet("sheet1")

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True

    # column header names, you can use your own headers here
    columns = ['Year', 'Term', 'Code', 'Subject', 'Teachers', 'Section(s)',
               'Form(s)', 'Language(s)', '# Students (prev. year)', '# TAs (theory)', '# TAs (requested)', '# TAs (approved)', '# TAs (hired)', '# TAs (to be filled)']

    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    for course in courses:
        row_num = row_num + 1
        ws.write(row_num, 0, course.year, font_style)
        ws.write(row_num, 1, course.term, font_style)
        ws.write(row_num, 2, course.code, font_style)
        ws.write(row_num, 3, course.subject, font_style)
        teacher_value = ''
        for teacher in course.teachers.all():
            teacher_value += "{last}, {first}\n".format(
                first=teacher.first_name, last=teacher.last_name)
        ws.write(row_num, 4, teacher_value, font_style)

        for teacher in course.teachers.all():
            section_result_list = list()
            if teacher.section_id:
                section_result_list.append(sections_dict[teacher.section_id])
        section_result_list = list(set(section_result_list))
        section_result = " / ".join(section_result_list)
        ws.write(row_num, 5, section_result, font_style)

        forms_value = ''
        if course.has_course:
            forms_value += "course\n"
        if course.has_exercises:
            forms_value += "exercises\n"
        if course.has_project:
            forms_value += "project\n"
        if course.has_practical_work:
            forms_value += "practical work\n"
        ws.write(row_num, 6, forms_value, font_style)
        languages_value = ''
        if course.taughtInFrench:
            languages_value += "French\n"
        if course.taughtInEnglish:
            languages_value = 'English\n'
        if course.taughtInGerman:
            languages_value += "German\n"
        ws.write(row_num, 7, languages_value, font_style)
        ws.write(row_num, 8, course.numberOfStudents, font_style)
        ws.write(row_num, 9, course.calculatedNumberOfTAs)
        ws.write(row_num, 10, course.requestedNumberOfTAs)
        ws.write(row_num, 11, course.approvedNumberOfTAs)
        ws.write(row_num, 12, course.applications_accepted)
        ws.write(row_num, 13, xlwt.Formula(
            "L{}-M{}".format(row_num+1, row_num+1)))

    # Create the totals of the columns
    row_num+=1
    ws.write(row_num, 7, "Total")
    ws.write(row_num, 8, xlwt.Formula("SUM(I2:I{})".format(row_num)))
    ws.write(row_num, 9, xlwt.Formula("SUM(J2:J{})".format(row_num)))
    ws.write(row_num, 10, xlwt.Formula("SUM(K2:K{})".format(row_num)))
    ws.write(row_num, 11, xlwt.Formula("SUM(L2:L{})".format(row_num)))
    ws.write(row_num, 12, xlwt.Formula("SUM(M2:M{})".format(row_num)))
    ws.write(row_num, 13, xlwt.Formula("SUM(N2:N{})".format(row_num)))

    wb.save(response)
    return response


@is_staff()
def phds_report(request):
    year = config.get_config('current_year')
    term = config.get_config('current_term')

    phds_info = dict()
    phds_ids = list()

    # Get base information about the phd
    phds = Group.objects.get(name="phds").user_set.all()
    for phd in phds:
        phd_to_add = dict()
        phd_to_add['id'] = phd.id
        phd_to_add['sciper'] = phd.sciper
        phd_to_add['first_name'] = phd.first_name
        phd_to_add['last_name'] = phd.last_name
        phds_info[phd.id] = phd_to_add
        phds_ids.append(phd.id)

    # Get the profile information about the phds
    availabilities = Availability.objects.filter(
        year=year, person_id__in=phds_ids).all()
    for availability in availabilities:
        phds_info[availability.person_id]['availability'] = availability.availability

    # Add the missing information about the availabilities
    for phd in phds_info:
        if 'availability' not in phds_info[phd]:
            phds_info[phd]['availability'] = ''

    # Get the courses ids in order to find the applications for them
    courses_ids_queryset = Course.objects.filter(
        year=year, term=term).values('id').all()
    courses_ids_list = list()
    [courses_ids_list.append(item['id']) for item in courses_ids_queryset]

    # Retrieve all the applications for the PhD students for the current courses
    applications = Applications.objects.filter(
        course_id__in=courses_ids_list, applicant_id__in=phds_ids).all()

    # Flag the PhDs with the correct information
    for application in applications:
        if application.status == 'Pending':
            if 'applications_pending' in phds_info[application.applicant_id]:
                phds_info[application.applicant_id]['applications_pending'] += 1
            else:
                phds_info[application.applicant_id]['applications_pending'] = 1
        elif application.status == 'Hired':
            if 'applications_accepted' in phds_info[application.applicant_id]:
                phds_info[application.applicant_id]['applications_accepted'] += 1
            else:
                phds_info[application.applicant_id]['applications_accepted'] = 1
        elif application.status == 'Rejected':
            if 'applications_declined' in phds_info[application.applicant_id]:
                phds_info[application.applicant_id]['applications_declined'] += 1
            else:
                phds_info[application.applicant_id]['applications_declined'] = 1
        elif application.status == 'Withdrawn':
            if 'applications_withdrawn' in phds_info[application.applicant_id]:
                phds_info[application.applicant_id]['applications_withdrawn'] += 1
            else:
                phds_info[application.applicant_id]['applications_withdrawn'] = 1

    # Add the missing information about the applications
    for phd in phds_info:
        if 'applications_pending' not in phds_info[phd]:
            phds_info[phd]['applications_pending'] = ''
        if 'applications_accepted' not in phds_info[phd]:
            phds_info[phd]['applications_accepted'] = ''
        if 'applications_declined' not in phds_info[phd]:
            phds_info[phd]['applications_declined'] = ''
        if 'applications_withdrawn' not in phds_info[phd]:
            phds_info[phd]['applications_withdrawn'] = ''

    context = {
        'phds': phds_info.values
    }

    return render(request, 'web/reports/phds_list.html', context)


@is_staff()
def download_phds_report(request):
    year = config.get_config('current_year')
    term = config.get_config('current_term')

    phds_info = dict()
    phds_ids = list()

    # Get base information about the phd
    phds = Group.objects.get(name="phds").user_set.all()
    for phd in phds:
        phd_to_add = dict()
        phd_to_add['id'] = phd.id
        phd_to_add['sciper'] = phd.sciper
        phd_to_add['first_name'] = phd.first_name
        phd_to_add['last_name'] = phd.last_name
        phd_to_add['email'] = phd.email
        phds_info[phd.id] = phd_to_add
        phds_ids.append(phd.id)

    # Get the profile information about the phds
    availabilities = Availability.objects.filter(
        year=year, person_id__in=phds_ids).all()
    for availability in availabilities:
        phds_info[availability.person_id]['availability'] = availability.availability

    # Add the missing information about the availabilities
    for phd in phds_info:
        if 'availability' not in phds_info[phd]:
            phds_info[phd]['availability'] = ''

    # Get the courses ids in order to find the applications for them
    courses_ids_queryset = Course.objects.filter(
        year=year, term=term).values('id').all()
    courses_ids_list = list()
    [courses_ids_list.append(item['id']) for item in courses_ids_queryset]

    # Retrieve all the applications for the PhD students for the current courses
    applications = Applications.objects.filter(
        course_id__in=courses_ids_list, applicant_id__in=phds_ids).all()

    # Flag the PhDs with the correct information
    for application in applications:
        if application.status == 'Pending':
            if 'applications_pending' in phds_info[application.applicant_id]:
                phds_info[application.applicant_id]['applications_pending'] += 1
            else:
                phds_info[application.applicant_id]['applications_pending'] = 1
        elif application.status == 'Hired':
            if 'applications_accepted' in phds_info[application.applicant_id]:
                phds_info[application.applicant_id]['applications_accepted'] += 1
            else:
                phds_info[application.applicant_id]['applications_accepted'] = 1
        elif application.status == 'Rejected':
            if 'applications_declined' in phds_info[application.applicant_id]:
                phds_info[application.applicant_id]['applications_declined'] += 1
            else:
                phds_info[application.applicant_id]['applications_declined'] = 1
        elif application.status == 'Withdrawn':
            if 'applications_withdrawn' in phds_info[application.applicant_id]:
                phds_info[application.applicant_id]['applications_withdrawn'] += 1
            else:
                phds_info[application.applicant_id]['applications_withdrawn'] = 1

    # Add the missing information about the applications
    for phd in phds_info:
        if 'applications_pending' not in phds_info[phd]:
            phds_info[phd]['applications_pending'] = ''
        if 'applications_accepted' not in phds_info[phd]:
            phds_info[phd]['applications_accepted'] = ''
        if 'applications_declined' not in phds_info[phd]:
            phds_info[phd]['applications_declined'] = ''
        if 'applications_withdrawn' not in phds_info[phd]:
            phds_info[phd]['applications_withdrawn'] = ''

    # Time to build the excel file
    # content-type of response
    response = HttpResponse(content_type='application/ms-excel')

    # decide file name
    response['Content-Disposition'] = 'attachment; filename="phds_report_{year}_{term}.xls"'.format(
        year=year, term=term)

    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')

    # adding sheet
    ws = wb.add_sheet("sheet1")

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True

    # column header names, you can use your own headers here
    columns = ['sciper',
               'first name',
               'last name',
               'email',
               'availability',
               'pending applications',
               'accepted applications',
               'declined applications',
               'withdrawn applications']

    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    for key, phd in phds_info.items():
        row_num = row_num + 1
        ws.write(row_num, 0, phd['sciper'], font_style)
        ws.write(row_num, 1, phd['first_name'], font_style)
        ws.write(row_num, 2, phd['last_name'], font_style)
        ws.write(row_num, 3, phd['email'], font_style)
        ws.write(row_num, 4, phd['availability'], font_style)
        ws.write(row_num, 5, phd['applications_pending'], font_style)
        ws.write(row_num, 6, phd['applications_accepted'], font_style)
        ws.write(row_num, 7, phd['applications_declined'], font_style)
        ws.write(row_num, 8, phd['applications_withdrawn'], font_style)
    wb.save(response)
    return response
