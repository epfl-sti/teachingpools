# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import re
from datetime import date, datetime
import datetime
from functools import wraps

import pandas as pd
import xlwt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import ExpressionWrapper, F, IntegerField, Prefetch, Q, Value
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
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
        elif u.groups.filter(name="teachers").exists():
            return True
        else:
            raise PermissionDenied

    return user_passes_test(has_staff_or_teacher_profile)


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""

    def in_groups(u):
        logger.debug(
            "Checking if %s is member of the '%s' group(s)", u.username, group_names
        )
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        raise PermissionDenied

    return user_passes_test(in_groups)


@is_superuser()
def get_courses(request):
    pass


@is_superuser()
def new_application(request):
    context = {}
    return render(request, "web/applications/new.html", context=context)


@is_superuser()
def get_applicants(request):
    if request.is_ajax():
        term = request.GET.get("term", None)
        data = []
        phds = Group.objects.get(name="phds").user_set.all()
        if term:
            phds = phds.filter(
                Q(last_name__icontains=term)
                | Q(first_name__icontains=term)
                | Q(sciper__icontains=term)
            ).all()
        for phd in phds:
            current_entry = {
                "id": phd.pk,
                "text": "{}, {} ({})".format(phd.last_name, phd.first_name, phd.sciper),
            }
            data.append(current_entry)
        response = {"items": data}
        return JsonResponse(response)


@is_superuser()
def get_courses(request):
    if request.is_ajax():
        term = request.GET.get("term", None)
        data = []
        courses = Course.objects.order_by("year", "term").all()
        if term:
            courses = (
                courses.filter(Q(subject__icontains=term) | Q(code__icontains=term))
                .order_by("year", "term")
                .all()
            )

        previous_group_text = ""
        current_group = None

        for course in courses:
            current_group_text = "{} - {}".format(course.year, course.term)
            if current_group_text != previous_group_text:
                if current_group:
                    data.append(current_group)
                current_group = {"text": current_group_text, "children": []}
                previous_group_text = current_group_text

            current_entry = {
                "id": course.pk,
                "text": "{} ({})".format(course.subject, course.code),
            }
            current_group["children"].append(current_entry)

        response = {"items": data}
        return JsonResponse(response)


@is_superuser()
def get_applications_statuses(request):
    if request.is_ajax():
        result = []
        for status in Applications.STATUS_CHOICES:
            result.append({"id": status[0], "text": status[1]})
        return JsonResponse({"items": result})


@is_superuser()
def save_application_endpoint(request):
    if request.is_ajax():
        applicant_id = request.POST.get("applicant", None)
        course_id = request.POST.get("course", None)
        status = request.POST.get("status", None)

        try:
            applicant = Person.objects.get(pk=applicant_id)
            course = Course.objects.get(pk=course_id)
            application, created = Applications.objects.get_or_create(
                applicant=applicant, course=course
            )
            application.applicant = applicant
            application.course = course
            application.createdAt = now()
            application.createdBy = request.user
            application.status = status
            application.closedAt = now()
            application.closedBy = request.user
            application.save()

            operation_status = "ok"
            if created == True:
                msg = "Application successfully created"
            else:
                msg = "Application successfully updated"
        except Exception as ex:
            logger.exception("Unable to save application")
            operation_status = "error"
            msg = str(ex)

        return JsonResponse({"status": operation_status, "msg": msg})


@is_superuser()
def get_applications_html(request):
    applications = (
        Applications.objects.all()
        .order_by("-openedAt")
        .select_related("applicant", "course",)
    )
    context = {"applications": applications}
    return render(request, "web/applications/list.html", context=context)


@is_superuser()
def delete_application_endpoint(request):
    if request.is_ajax():
        id = request.POST.get("id", None)
        application = Applications.objects.get(pk=id)
        application.delete()
        msg = "ok"
        return JsonResponse({"msg": msg, "id": id})

