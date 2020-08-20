# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import re
from datetime import date, datetime
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


@is_staff()
def get_mail_campaigns(request):
    campaigns = Mail_campaign.objects.order_by("-created_at").all()
    context = {"campaigns": campaigns}
    return render(request, "web/mailer/list.html", context=context)


@is_staff()
def get_campaign_details(request, id):
    campaign = get_object_or_404(Mail_campaign, pk=id)
    emails = Mail_message.objects.filter(campaign=campaign).all()
    context = {"emails": emails}
    return render(request, "web/mailer/campaign_details.html", context=context)


@is_staff()
def new_mailer_campaign(request):
    context = {}
    return render(request, "web/forms/mailer/new_campaign.html", context=context)


@is_staff()
def new_mailer_campaign_post(request):
    if request.is_ajax():
        to = request.POST.get("to", None)
        subject = request.POST.get("subject", None)
        message = request.POST.get("message", None)

        if to:
            emails = to.split("\n")

            campaign = Mail_campaign()
            campaign.created_by = request.user
            campaign.to = to
            campaign.subject = "[STI Teaching Assistants] {}".format(subject)
            campaign.message = message
            campaign.save()

            for email in emails:
                mail = Mail_message()
                mail.campaign = campaign
                mail.created_by = request.user
                mail.to = email
                mail.subject = "[STI Teaching Assistants] {}".format(subject)
                mail.message = message
                mail.save()

            response = {
                "msg": "Your message has been submitted and will be sent shortly."
            }
            messages.success(request, "The mail campaign has been successfully submitted. It should be distributed shortly.")
            return JsonResponse(response)
