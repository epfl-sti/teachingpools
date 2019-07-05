# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
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


def impersonable(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if settings.DEBUG:
            username_to_impersonate = request.GET.get('impersonate', None)
            if username_to_impersonate:
                logger.info("impersonating %s", username_to_impersonate)

                try:
                    user_to_impersonate = User.objects.get(
                        username=username_to_impersonate)
                    if user_to_impersonate and user_to_impersonate != request.user:
                        login(request, user_to_impersonate,
                              backend='django.contrib.auth.backends.ModelBackend')
                        messages.info(request, mark_safe("<i class='fas fa-info-circle'></i>&nbsp;Current user switched to {} {}".format(
                            user_to_impersonate.first_name, user_to_impersonate.last_name)))
                except Exception as ex:
                    messages.error(request, mark_safe(
                        "<i class='fas fa-exclamation-circle'></i>&nbsp;Unable to switch user. Please check the username you want to use."))

        return function(request, *args, **kwargs)
    return wrap


@login_required
@impersonable
def index(request):
    if request.user.is_staff and NumberOfTAUpdateRequest.objects.filter(status="Pending").exists():
        messages.info(
            request, mark_safe("<i class='fas fa-info-circle'></i>&nbsp;You have (a) pending <a href='{}'>TA request(s) to validate</a>".format(reverse('web:get_TAs_requests_to_validate'))))

    year = settings.APP_CURRENT_YEAR
    if request.user.groups.filter(name='phds').exists() and not Availability.objects.filter(year=year, person=request.user).exists():
        message = mark_safe(
            "<i class='fas fa-info-circle'></i>&nbsp;You should <a href='{}'>update your profile</a>.".format(reverse('web:update_my_profile')))
        messages.info(request, message)
    return render(request, 'web/index.html')


@impersonable
def courses_full_list(request, year):
    all_courses = Course.objects.filter(
        year=year).prefetch_related('teachers').all()
    user_is_phd = request.user.groups.filter(name="phds").exists()
    if user_is_phd:
        courses_applied_to = [application.course.pk for application in Applications.objects.filter(
            applicant=request.user).all()]
    else:
        courses_applied_to = []

    context = {
        'courses': all_courses,
        'user_is_phd': user_is_phd,
        'courses_applied_to': courses_applied_to,
    }
    return render(request, 'web/all_courses.html', context)


@login_required
@impersonable
@group_required('teachers')
def courses_list_year_teacher(request, year):
    teachings = Teaching.objects.filter(
        person=request.user).prefetch_related('course').all()
    context = {
        'teachings': teachings
    }
    return render(request, 'web/prof_courses.html', context)


@login_required
@impersonable
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


@login_required
@impersonable
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


@login_required
@impersonable
@group_required('teachers')
def requests_for_tas_teacher(request):
    requests = NumberOfTAUpdateRequest.objects.filter(
        requester=request.user).prefetch_related('course').order_by('openedAt').all()
    context = {
        'requests': requests
    }
    return render(request, 'web/prof_ta_requests.html', context)


@login_required
@impersonable
@group_required('teachers')
def requests_for_tas_teacher_status(request, status):
    requests = NumberOfTAUpdateRequest.objects.filter(
        requester=request.user, status=status.capitalize()).prefetch_related('course').order_by('openedAt').all()
    context = {
        'requests': requests
    }
    return render(request, 'web/prof_ta_requests.html', context)


@login_required
@impersonable
@group_required('teachers')
def request_for_TA(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

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
            ta_request.save()
            messages.success(
                request, "Your request for TAs has been successfully saved")
            return HttpResponseRedirect(reverse('web:courses_list_year_teacher', args=[settings.APP_CURRENT_YEAR]))

    context = {
        'course_id': course_id,
        'course': course,
        'form': form
    }
    return render(request, 'web/request_for_ta_form.html', context)


@login_required
@impersonable
@is_staff()
def get_TAs_requests_to_validate(request):
    requests = NumberOfTAUpdateRequest.objects.filter(status='Pending').all()
    context = {
        'requests': requests
    }
    return render(request, 'web/requests_for_tas.html', context)


@login_required
@impersonable
@is_staff()
def validate_request_for_TA(request, request_id):
    if request.method == 'POST':
        form = RequestForTAApproval(request.POST)
        if form.is_valid():
            if 'Approve' in request.POST:
                status = "Approved"
            elif 'Reject' in request.POST:
                status = "Rejected"

            request_obj = NumberOfTAUpdateRequest.objects.get(
                pk=form.cleaned_data['request_id'])
            request_obj.status = status
            request_obj.decisionReason = form.cleaned_data['reason_for_decision']
            request_obj.closedAt = now()
            person = request.user
            request_obj.decidedBy = request.user
            request_obj.save()

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


@login_required
@impersonable
@group_required('teachers')
def view_request_for_TA(request, request_id):
    ta_request = NumberOfTAUpdateRequest.objects.get(pk=request_id)
    form = RequestForTAView()
    form.fields['request_id'].initial = ta_request.pk
    form.fields['opened_at'].initial = ta_request.openedAt
    form.fields['requester'].initial = "{}, {}".format(
        ta_request.requester.last_name, ta_request.requester.first_name)
    form.fields['course'].initial = "{} ({})".format(
        ta_request.course.subject, ta_request.course.code)
    form.fields['requestedNumberOfTAs'].initial = ta_request.requestedNumberOfTAs
    form.fields['reason_for_request'].initial = ta_request.requestReason
    form.fields['reason_for_decision'].initial = ta_request.decisionReason

    course = ta_request.course
    context = {
        'course': course,
        'request_id': request_id,
        'form': form
    }

    return render(request, 'web/request_for_ta_view_form.html', context)


@login_required
@impersonable
@group_required('phds')
def apply(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

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


@login_required
@impersonable
@group_required('phds')
def update_my_profile(request):
    year = settings.APP_CURRENT_YEAR

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


@login_required
@impersonable
@group_required('phds')
def my_applications(request):
    applications = Applications.objects.filter(
        applicant=request.user).prefetch_related('course').all()
    context = {
        'applications': applications,
    }
    return render(request, 'web/applications.html', context)
