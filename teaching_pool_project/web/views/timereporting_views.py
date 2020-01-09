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
def add_time_report(request):
    timereporting = TimeReport()
    timereporting_form = TimeReportForm(request.POST or None, instance=timereporting, user=request.user)

    if request.method == 'POST':
        if timereporting_form.is_valid():
            logger.info(timereporting_form.cleaned_data.get('year'))
            pass
        else:
            messages.error(request, "Please correct the errors below and resubmit.")

    context = {
        'form': timereporting_form,
    }

    return render(request, 'web/forms/timereporting/add.html', context)


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
