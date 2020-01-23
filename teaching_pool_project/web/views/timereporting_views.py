# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import re
from functools import wraps

import xlwt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core import serializers
from django.db.models import Prefetch, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template import Context
from django.template.loader import get_template
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.views import generic

from epfl.sti.helpers import ldap as epfl_ldap
from web.forms.timereporting_forms import *
from web.helpers import config
from web.models import *

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


@group_required('phds')
def get_time_reports(request):
    context = {}
    return render(request, 'web/timereporting/list.html', context)


@group_required('phds')
def add_time_report(request):
    time_reporting_is_open = config.get_config('time_reporting_is_open')
    if time_reporting_is_open == False:
        messages.error(request, "You are not allowed to enter new time reporting entries at the moment.")
        raise PermissionDenied

    timereporting = TimeReport(created_by=request.user)
    timereporting_form = TimeReportForm(request.POST or None, instance=timereporting, user=request.user)

    if request.method == 'POST':
        if timereporting_form.is_valid():
            timereporting.save()
            messages.success(request, "Time reporting entry successfully saved.")
            return redirect('web:get_time_reports')
        else:
            messages.error(request, "Please correct the errors below and resubmit.")

    context = {
        'action': 'Add',
        'form': timereporting_form,
    }

    return render(request, 'web/forms/timereporting/add.html', context)


@group_required('phds')
def delete_time_report(request, id):
    try:
        time_report = TimeReport.objects.get(pk=id)
    except ObjectDoesNotExist:
        messages.error(request, "Unable to find the time report in the database")
        return redirect('web:get_time_reports')

    if time_report.created_by != request.user:
        messages.error(request, "You are not allowed to delete this entry")
        raise PermissionDenied
    else:
        time_report.delete()
        messages.success(request, "Entry successfully deleted")
        return redirect('web:get_time_reports')


@group_required('phds')
def edit_time_report(request, id):
    try:
        time_report = TimeReport.objects.get(pk=id)
    except ObjectDoesNotExist:
        messages.error(request, "Unable to find the time report in the database")
        return redirect('web:time_reports')

    if time_report.created_by != request.user:
        messages.error(request, "You are not allowed to edit this entry")
        raise PermissonDenied

    time_report_form = TimeReportForm(request.POST or None, instance=time_report, user=request.user)

    if request.method == 'POST':
        if time_report_form.is_valid():
            time_report.save()
            messages.success(request, "Time reporting entry successfully edited.")
            return redirect('web:get_time_reports')
        else:
            messages.error(request, "PLease correct the errors below and resubmit.")

    context = {
        'action': 'Edit',
        'form': time_report_form,
    }

    return render(request, 'web/forms/timereporting/add.html', context)


@group_required('phds')
def get_user_time_reports(request):
    if request.is_ajax():
        entries = TimeReport.objects.filter(created_by=request.user).all()
        return_value = serializers.serialize('json', entries)
    else:
        return_value = 'fail'

    mimetype = "application/json"
    return HttpResponse(return_value, mimetype)


@group_required('phds')
def autocomplete_my_courses(request):
    if request.is_ajax():
        q = request.GET.get('term', '')

        # get all the courses for which the user has been hired
        applications = Applications.objects.filter(applicant=request.user, status="Hired").select_related('course').all()
        courses_ids = []
        [courses_ids.append(application.course.id) for application in applications]
        courses = Course.objects.filter(Q(code__icontains=q) | Q(subject__icontains=q), id__in=courses_ids).all()

        return_value = list()
        [return_value.append("{} ({} / {} / {})".format(course.subject, course.year, course.term, course.code)) for course in courses]
        return_value = json.dumps(return_value)
    else:
        return_value = 'fail'

    mimetype = 'application/json'
    return HttpResponse(return_value, mimetype)


@group_required('phds')
def autocomplete_all_teachers(request):
    if request.is_ajax:
        q = request.GET.get('term', '')
        teachers = Group.objects.get(name="teachers").user_set.all()
        persons_ids = []
        [persons_ids.append(person.id) for person in teachers]
        persons = Person.objects.filter(Q(last_name__icontains=q) | Q(first_name__icontains=q), id__in=persons_ids)
        return_value = list()
        [return_value.append("{}, {} ({})".format(person.last_name, person.first_name, person.sciper)) for person in persons]
        return_value = json.dumps(return_value)
    else:
        return_value = 'fail'

    mimetype = 'application/json'
    return HttpResponse(return_value, mimetype)


@group_required('phds')
def autocomplete_all_students(request):
    if request.is_ajax:
        q = request.GET.get('term', '')
        students = epfl_ldap.get_students_by_partial_first_name_or_partial_last_name(settings, q, q)
        return_value = list()
        [return_value.append("{}, {} ({})".format(student['last_name'], student['first_name'], student['sciper'])) for student in students]
        return_value = json.dumps(return_value)
    else:
        return_value = 'fail'

    mimetype = "application/json"
    return HttpResponse(return_value, mimetype)


@group_required('phds')
def autocomplete_all_units(request):
    if request.is_ajax:
        q = request.GET.get('term', '')
        units = epfl_ldap.get_units_by_partial_name_or_partial_last_acronym(settings, q)
        return_value = json.dumps(units)
    else:
        return_value = 'fail'

    mimetype = "application/json"
    return HttpResponse(return_value, mimetype)


@group_required('phds')
def get_teacher(request, id):
    if request.is_ajax():
        person = get_object_or_404(Person, pk=id)
        if not person.groups.filter(name='teachers').exists():
            return_value = ''
        else:
            return_value = serializers.serialize('json', [person], fields=['first_name', 'last_name'])
    else:
        return_value = 'fail'

    mimetype = 'application/json'
    return HttpResponse(return_value, mimetype)


@group_required('phds')
def get_course(request, id):
    if request.is_ajax():
        course = get_object_or_404(Course, pk=id)
        return_value = serializers.serialize('json', [course], fields=['year', 'term', 'code', 'subject'])
    else:
        return_value = 'fail'

    mimetype = 'application/json'
    return HttpResponse(return_value, mimetype)
