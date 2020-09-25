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
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import Context
from django.template.loader import get_template
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.views import generic

from epfl.sti.helpers import ldap as epfl_ldap
from web.helpers import config

from web.forms.forms import *
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


def index(request):
    year = config.get_config("current_year")
    term = config.get_config("current_term")
    if term == "HIVER":
        term = "winter"
    elif term == "ETE":
        term = "summer"
    else:
        pass

    if (
        request.user.is_staff
        and NumberOfTAUpdateRequest.objects.filter(status="Pending").exists()
    ):
        messages.info(
            request,
            mark_safe(
                "<i class='fas fa-info-circle'></i>&nbsp;You have (a) pending <a href='{}'>TA request(s) to validate</a>".format(
                    reverse("web:get_TAs_requests_to_validate")
                )
            ),
        )

    if (
        request.user.groups.filter(name="phds").exists()
        and not Availability.objects.filter(
            year=year, term=term, person=request.user
        ).exists()
    ):
        message = mark_safe(
            "<i class='fas fa-info-circle'></i>&nbsp;You should <a href='{}'>update your profile</a>.".format(
                reverse("web:update_my_profile")
            )
        )
        messages.info(request, message)
    return render(request, "web/index.html")


def courses_full_list(request, year):
    year = config.get_config("current_year")
    term = config.get_config("current_term")

    all_courses = (
        Course.objects.filter(year=year, term=term).prefetch_related("teachers").all()
    )
    user_is_phd = request.user.groups.filter(name="phds").exists()
    if user_is_phd:
        courses_applied_to = [
            application.course.pk
            for application in Applications.objects.filter(applicant=request.user).all()
        ]
    else:
        courses_applied_to = []

    messages.info(
        request,
        mark_safe(
            "<i class='fas fa-sticky-note'></i>&nbsp;Study plans: <a href='https://edu.epfl.ch/studyplan/en/bachelor' target=^_blank'>bachelor</a>, <a href='https://edu.epfl.ch/studyplan/en/master' target='_blank'>master</a>"
        ),
    )
    context = {
        "year": year,
        "courses": all_courses,
        "user_is_phd": user_is_phd,
        "courses_applied_to": courses_applied_to,
    }
    return render(request, "web/all_courses.html", context)


@group_required("teachers")
def courses_list_year_teacher(request, year):
    year = config.get_config("current_year")
    term = config.get_config("current_term")

    courses = (
        Course.objects.filter(year=year, term=term, teachers=request.user)
        .prefetch_related("teachers")
        .all()
    )

    context = {
        "courses": courses,
    }
    return render(request, "web/prof_courses.html", context)


@group_required("teachers")
def get_applications_for_my_courses(request):
    if request.is_ajax():
        teachings = (
            Teaching.objects.filter(person=request.user)
            .prefetch_related("course")
            .all()
        )
        courses_ids = [item.course.pk for item in teachings]
        applications = (
            Applications.objects.filter(course_id__in=courses_ids)
            .select_related("course")
            .all()
        )
        data = []
        for application in applications:
            current_application = {}
            current_application["year"] = application.course.year
            current_application["term"] = application.course.term
            current_application["subject"] = application.course.subject
            current_application["code"] = application.course.code
            current_application["first_name"] = application.applicant.first_name
            current_application["last_name"] = application.applicant.last_name
            current_application["email"] = application.applicant.email
            current_application["status"] = application.status
            current_application["applicant_profile_url"] = reverse(
                "web:view_profile", args=[application.applicant.pk]
            )
            current_application["application_review_url"] = reverse(
                "web:review_application", args=[application.pk]
            )
            data.append(current_application)

        response = {"applications": data}
        return JsonResponse(response)

    context = {"STATIC_URL": settings.STATIC_URL}
    return render(request, "web/applications_to_my_courses.html", context)


@group_required("teachers")
def review_application(request, application_id):
    application = get_object_or_404(Applications, pk=application_id)
    application_form = ApplicationForm_teacher(
        request.POST or None, instance=application
    )

    if request.method == "POST":
        if "Approve" in request.POST:
            status = "Hired"
        elif "Reject" in request.POST:
            status = "Rejected"

        if application_form.is_valid():

            application_form.save(commit=False)
            application.status = status
            application.closedAt = now()
            application.closedBy = request.user
            if application_form.cleaned_data["decisionReason"]:
                application.decisionReason = application_form.cleaned_data[
                    "decisionReason"
                ]
            application.save()
            messages.success(request, "Your decision has been recorded")
            return HttpResponseRedirect(reverse("web:applications_for_my_courses"))

    context = {
        "course": application.course,
        "person": application.applicant,
        "form": application_form,
        "application_id": application.pk,
    }

    return render(request, "web/application_review_form.html", context)


@group_required("teachers")
def requests_for_tas_teacher(request):
    requests = (
        NumberOfTAUpdateRequest.objects.filter(requester=request.user)
        .prefetch_related("course")
        .order_by("openedAt")
        .all()
    )
    context = {"requests": requests}
    return render(request, "web/prof_ta_requests.html", context)


@group_required("teachers")
def requests_for_tas_teacher_status(request, status):
    requests = (
        NumberOfTAUpdateRequest.objects.filter(
            requester=request.user, status=status.capitalize()
        )
        .prefetch_related("course")
        .order_by("openedAt")
        .all()
    )
    context = {"requests": requests}
    return render(request, "web/prof_ta_requests.html", context)


@group_required("teachers")
def request_for_TA(request, course_id):
    if not config.get_config("requests_for_TAs_are_open"):
        messages.error(
            request, "The requests for Teaching Assistants are not open at the moment."
        )
        return render(request, "web/blank.html")

    course = get_object_or_404(Course, pk=course_id)

    year = config.get_config("current_year")
    term = config.get_config("current_term")
    if course.year != year or course.term != term:
        messages.error(
            request,
            "The requests for Teaching Assistants are not open for this year / term",
        )
        return render(request, "web/blank.html")

    try:
        ta_request = NumberOfTAUpdateRequest.objects.get(
            status="Pending", course=course
        )
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
            ta_request.requestedNumberOfTAs = form.cleaned_data["requestedNumberOfTAs"]
            ta_request.requestReason = form.cleaned_data["requestReason"]
            ta_request.save_and_notify()
            messages.success(
                request, "Your request for TAs has been successfully saved"
            )
            return HttpResponseRedirect(
                reverse(
                    "web:courses_list_year_teacher",
                    args=[config.get_config("current_year")],
                )
            )

    context = {"course_id": course_id, "course": course, "form": form}
    return render(request, "web/request_for_ta_form.html", context)


@group_required("teachers")
def accept_theoretical_number_of_tas(request, course_id):
    # General authorization setting check if the requests for TAs are open
    if not config.get_config("requests_for_TAs_are_open"):
        messages.error(
            request, "The requests for Teaching Assistants are not open at the moment."
        )
        return render(request, "web/blank.html")

    # TODO: Add a check if the teacher accessing the request screen is actually teaching this course

    # Check if the request is for a course for the current period
    course = get_object_or_404(Course, pk=course_id)
    year = config.get_config("current_year")
    term = config.get_config("current_term")
    if course.year != year or course.term != term:
        messages.error(
            request,
            "The requests for Teaching Assistants are not open for this year / term",
        )
        return render(request, "web/blank.html")

    # Then we should check if there are already requests pending for this course
    try:
        # find a currently pending request for TAs
        ta_request = NumberOfTAUpdateRequest.objects.get(
            status="Pending", course=course
        )
    except ObjectDoesNotExist:
        # if it does not exist, create a simple boilerplate
        ta_request = NumberOfTAUpdateRequest()
        ta_request.course = course
        ta_request.requester = request.user
        ta_request.openedAt = now()

    # Since this request will supercede any pending one, update the details of the request.
    ta_request.requestedNumberOfTAs = course.calculatedNumberOfTAs
    ta_request.requestReason = "approved theoretical number of TAs"
    ta_request.closedAt = now()
    ta_request.decisionReason = (
        "Auto accepted since it was a simple approval of the theoretical number of TAs"
    )
    ta_request.status = "Approved"
    ta_request.save()
    ta_request.update_related_course(action="approved")
    ta_request.send_mail_on_TAs_requested(action="approved")

    messages.success(request, "Your request for TAs has been successfully saved")
    return HttpResponseRedirect(
        reverse(
            "web:courses_list_year_teacher", args=[config.get_config("current_year")]
        )
    )


@is_staff()
def get_TAs_requests_to_validate(request):
    requests = NumberOfTAUpdateRequest.objects.filter(status="Pending").all()
    sections = Section.objects.all()
    context = {
        "requests": requests,
        "sections": sections,
    }
    return render(request, "web/requests_for_tas.html", context)


@is_staff()
def validate_request_for_TA(request, request_id):
    if request.method == "POST":
        form = RequestForTAApproval(request.POST)
        if form.is_valid():
            if "Approve" in request.POST:
                status = "Approved"
            elif "Decline" in request.POST:
                status = "Declined"

            request_obj = NumberOfTAUpdateRequest.objects.get(
                pk=form.cleaned_data["request_id"]
            )
            request_obj.status = status
            request_obj.decisionReason = form.cleaned_data["reason_for_decision"]
            request_obj.closedAt = now()
            person = request.user
            request_obj.decidedBy = request.user
            request_obj.save_and_notify()

            return HttpResponseRedirect(reverse("web:get_TAs_requests_to_validate"))

    else:
        requestForTA = NumberOfTAUpdateRequest.objects.get(pk=request_id)
        form = RequestForTAApproval()
        form.fields["request_id"].initial = requestForTA.pk
        form.fields["opened_at"].initial = requestForTA.openedAt
        form.fields["requester"].initial = "{}, {}".format(
            requestForTA.requester.last_name, requestForTA.requester.first_name
        )
        form.fields["course"].initial = "{} ({})".format(
            requestForTA.course.subject, requestForTA.course.code
        )
        form.fields["requestedNumberOfTAs"].initial = requestForTA.requestedNumberOfTAs
        form.fields["reason_for_request"].initial = requestForTA.requestReason

        course = requestForTA.course
        context = {"request_id": request_id, "course": course, "form": form}
        return render(request, "web/request_for_ta_review_form.html", context)


@group_required("teachers")
def view_request_for_TA(request, request_id):
    ta_request = get_object_or_404(NumberOfTAUpdateRequest, pk=request_id)
    form = RequestForTAView()
    form.fields["request_id"].initial = ta_request.pk
    form.fields["opened_at"].initial = ta_request.openedAt
    form.fields["requester"].initial = "{}, {}".format(
        ta_request.requester.last_name, ta_request.requester.first_name
    )
    form.fields["course"].initial = "{} ({})".format(
        ta_request.course.subject, ta_request.course.code
    )
    form.fields["requestedNumberOfTAs"].initial = ta_request.requestedNumberOfTAs
    form.fields["reason_for_request"].initial = ta_request.requestReason
    form.fields["status"].initial = ta_request.status
    form.fields["reason_for_decision"].initial = ta_request.decisionReason

    course = ta_request.course
    context = {"course": course, "request_id": request_id, "form": form}

    return render(request, "web/request_for_ta_view_form.html", context)


@group_required("phds")
def apply(request, course_id):
    if not config.get_config("applications_are_open"):
        messages.error(
            request,
            "The applications for Teaching Assistants positions are not open at the moment.",
        )
        return render(request, "web/blank.html")

    course = get_object_or_404(Course, pk=course_id)

    year = config.get_config("current_year")
    term = config.get_config("current_term")
    if course.year != year or course.term != term:
        messages.error(
            request,
            "The applications for Teaching Assistants positions are not open for this year / term",
        )
        return render(request, "web/blank.html")

    # Check that the person does not have more than 3 pending applications
    number_of_pending_applications = Applications.objects.filter(
        course__year=year, course__term=term, status="Pending", applicant=request.user
    ).count()
    if number_of_pending_applications >= 3:
        messages.error(
            request, "You are not allowed to have more than 3 applications pending"
        )
        return render(request, "web/blank.html")
    try:
        application = Applications.objects.get(applicant=request.user, course=course)
    except ObjectDoesNotExist:
        application = Applications()
        application.course = course
        application.applicant = request.user

    application_form = ApplicationForm_phd(request.POST or None, instance=application)

    if request.method == "POST":
        if application_form.is_valid():
            application_form.save(commit=False)
            application.save()
            messages.success(request, "Your application has been submitted")
            return HttpResponseRedirect(
                reverse("web:courses_full_list", args=[course.year])
            )

    context = {"course": course, "form": application_form}

    return render(request, "web/application_form.html", context)


@group_required("phds")
def withdraw_application(request, application_id):
    if config.get_config("phds_can_withdraw_applications") == False:
        messages.error(request, "Applications cannot be withdrawn at the moment")
        raise PermissionDenied

    application = get_object_or_404(Applications, pk=application_id)

    if application.applicant != request.user:
        raise PermissionDenied

    application.status = "Withdrawn"
    application.closedBy = request.user
    application.closedAt = now()
    application.decisionReason = "Application withdrawn by the PhD"
    application.save()

    return HttpResponseRedirect(reverse("web:my_applications"))


@group_required("phds")
def update_my_profile(request):
    year = config.get_config("current_year")
    term = config.get_config("current_term")
    if term == "HIVER":
        term = "winter"
    elif term == "ETE":
        term = "summer"
    else:
        pass

    # Working with the availabilities
    availability, availability_created = Availability.objects.get_or_create(
        person=request.user, year=year, term=term
    )
    if availability_created:
        messages.warning(
            request,
            "Since you did not fill in your profile, your default availability has been set to 'Available'",
        )
    availability_form = AvailabilityForm(request.POST or None, instance=availability)

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
        languages_form = LanguagesForm(initial={"languages": languages})

    # Working with the topics
    topics_form = TopicForm(request.POST or None, instance=request.user)

    if request.method == "POST":
        complete_form_is_OK = True

        if availability_form.is_valid():
            availability_form.save(commit=False)
            availability.save()
        else:
            messages.error(
                request, "The availability section contains error. Please review it"
            )
            complete_form_is_OK = False

        if languages_form.is_valid():
            request.user.canTeachInFrench = (
                "f" in languages_form.cleaned_data["languages"]
            )
            request.user.canTeachInEnglish = (
                "e" in languages_form.cleaned_data["languages"]
            )
            request.user.canTeachInGerman = (
                "g" in languages_form.cleaned_data["languages"]
            )
            request.user.save()
        else:
            messages.error(
                request, "The languages section contains error. Please review it"
            )
            complete_form_is_OK = False

        # Topics
        if topics_form.is_valid():
            topics_form.save()

        else:
            messages.error(
                request,
                "The list of selected topics contains error(s). Please review it",
            )
            complete_form_is_OK = False

        if complete_form_is_OK:
            messages.success(request, "Your profile has been succesfully updated.")

    context = {
        "year": year,
        "term": term,
        "availability_form": availability_form,
        "languages_form": languages_form,
        "topics_form": topics_form,
    }
    return render(request, "web/profile.html", context)


@is_staff_or_teacher()
def view_profile(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    year = config.get_config("current_year")
    term = config.get_config("current_term")
    if term == "HIVER":
        term = "winter"
    elif term == "ETE":
        term = "summer"
    else:
        pass

    try:
        availability = Availability.objects.get(
            person_id=person_id, year=year, term=term
        ).availability
        unavailability_reason = Availability.objects.get(
            person_id=person_id, year=year, term=term
        ).reason
    except ObjectDoesNotExist:
        availability = "N/A"
        unavailability_reason = "N/A"

    try:
        topics = Interests.objects.filter(person=person).prefetch_related("topic").all()
        topics = [interest.topic.name for interest in topics]
        if len(topics) == 0:
            topics = "N/A"
        else:
            topics = ", ".join(topics)
    except ObjectDoesNotExist:
        topics = "N/A"

    languages = list()
    if person.canTeachInFrench:
        languages.append("French")
    if person.canTeachInEnglish:
        languages.append("English")
    if person.canTeachInGerman:
        languages.append("German")
    if len(languages) > 0:
        languages = ", ".join(languages)
    else:
        languages = "N/A"

    context = {
        "person": person,
        "availability": availability,
        "unavailability_reason": unavailability_reason,
        "topics": topics,
        "languages": languages,
    }
    return render(request, "web/profile_view.html", context)


@group_required("phds")
def my_applications(request):
    if request.is_ajax():
        applications = (
            Applications.objects.filter(applicant=request.user)
            .prefetch_related("course")
            .all()
        )
        data = []
        for application in applications:
            item = {}
            item["year"] = application.course.year
            item["term"] = application.course.term
            item["code"] = application.course.code
            item["subject"] = application.course.subject
            item["status"] = application.status
            item["decision_reason"] = application.decisionReason
            item["withdraw_url"] = reverse(
                "web:withdraw_application", args=[application.pk]
            )
            data.append(item)
        return JsonResponse(
            {
                "can_withdraw": config.get_config("phds_can_withdraw_applications"),
                "data": data,
            }
        )

    context = {
        "STATIC_URL": settings.STATIC_URL,
    }
    return render(request, "web/applications.html", context)


@is_staff()
def edit_config(request):
    config = Config.objects.first()
    if not config:
        config = Config()

    config_form = ConfigForm(request.POST or None, instance=config)

    if request.method == "POST":
        if config_form.is_valid():
            config_form.save()
            messages.success(request, "The configuration has been successfully saved")

    context = {
        "config_form": config_form,
    }

    return render(request, "web/config_form.html", context)


@is_staff()
def courses_report(request, year, term):

    courses = (
        Course.objects.filter(year=year, term=term).prefetch_related("teachers").all()
    )
    sections_dict = dict()
    sections_obj = Section.objects.values("id", "name").all()
    for section in sections_obj:
        sections_dict[section["id"]] = section["name"]

    context = {
        "year": year,
        "term": term,
        "sections": sections_dict,
        "courses": courses,
    }

    return render(request, "web/reports/courses_list.html", context)


@is_staff()
def download_course_report(request, year, term):

    courses = (
        Course.objects.filter(year=year, term=term).prefetch_related("teachers").all()
    )

    # Get base data about sections in order NOT TO re-query the DB for each teacher of each courses
    sections_obj = Section.objects.values("id", "name").all()
    sections_dict = dict()
    for section in sections_obj:
        sections_dict[section["id"]] = section["name"]

    # content-type of response
    response = HttpResponse(content_type="application/ms-excel")

    # decide file name
    response["Content-Disposition"] = 'attachment; filename="{year}_{term}.xls"'.format(
        year=year, term=term
    )

    # creating workbook
    wb = xlwt.Workbook(encoding="utf-8")

    # adding sheet
    ws = wb.add_sheet("sheet1")

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True

    # column header names, you can use your own headers here
    columns = [
        "Year",
        "Term",
        "Code",
        "Subject",
        "Teachers",
        "Section(s)",
        "Form(s)",
        "Language(s)",
        "# Students (prev. year)",
        "# TAs (theory)",
        "# TAs (requested)",
        "# TAs (approved)",
        "# Applications (received)",
        "# Applications (accepted)",
        "# Applications (declined)",
        "# Applications (withdrawn)",
        "# Applications (pending)",
        "# TAs (to be filled)",
    ]

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
        teacher_value = ""
        for teacher in course.teachers.all():
            teacher_value += "{last}, {first}\n".format(
                first=teacher.first_name, last=teacher.last_name
            )
        ws.write(row_num, 4, teacher_value, font_style)

        for teacher in course.teachers.all():
            section_result_list = list()
            if teacher.section_id:
                section_result_list.append(sections_dict[teacher.section_id])
        section_result_list = list(set(section_result_list))
        section_result = " / ".join(section_result_list)
        ws.write(row_num, 5, section_result, font_style)

        forms_value = ""
        if course.has_course:
            forms_value += "course\n"
        if course.has_exercises:
            forms_value += "exercises\n"
        if course.has_project:
            forms_value += "project\n"
        if course.has_practical_work:
            forms_value += "practical work\n"
        ws.write(row_num, 6, forms_value, font_style)
        languages_value = ""
        if course.taughtInFrench:
            languages_value += "French\n"
        if course.taughtInEnglish:
            languages_value = "English\n"
        if course.taughtInGerman:
            languages_value += "German\n"
        ws.write(row_num, 7, languages_value, font_style)
        ws.write(row_num, 8, course.numberOfStudents, font_style)
        ws.write(row_num, 9, course.calculatedNumberOfTAs)
        ws.write(row_num, 10, course.requestedNumberOfTAs)
        ws.write(row_num, 11, course.approvedNumberOfTAs)
        ws.write(row_num, 12, course.applications_received)
        ws.write(row_num, 13, course.applications_accepted)
        ws.write(row_num, 14, course.applications_rejected)
        ws.write(row_num, 15, course.applications_withdrawn)
        ws.write(
            row_num,
            16,
            xlwt.Formula(
                "M{}-N{}-O{}-P{}".format(
                    row_num + 1, row_num + 1, row_num + 1, row_num + 1
                )
            ),
        )
        ws.write(row_num, 17, xlwt.Formula("L{}-N{}".format(row_num + 1, row_num + 1)))

    # Create the totals of the columns
    row_num += 1
    ws.write(row_num, 7, "Total")
    ws.write(row_num, 8, xlwt.Formula("SUM(I2:I{})".format(row_num)))
    ws.write(row_num, 9, xlwt.Formula("SUM(J2:J{})".format(row_num)))
    ws.write(row_num, 10, xlwt.Formula("SUM(K2:K{})".format(row_num)))
    ws.write(row_num, 11, xlwt.Formula("SUM(L2:L{})".format(row_num)))
    ws.write(row_num, 12, xlwt.Formula("SUM(M2:M{})".format(row_num)))
    ws.write(row_num, 13, xlwt.Formula("SUM(N2:N{})".format(row_num)))
    ws.write(row_num, 14, xlwt.Formula("SUM(O2:O{})".format(row_num)))
    ws.write(row_num, 15, xlwt.Formula("SUM(P2:P{})".format(row_num)))
    ws.write(row_num, 16, xlwt.Formula("SUM(Q2:Q{})".format(row_num)))
    ws.write(row_num, 17, xlwt.Formula("SUM(R2:R{})".format(row_num)))

    wb.save(response)
    return response


@is_staff()
def phds_report(request, year, term):
    phds_info = dict()
    phds_ids = list()

    # Get base information about the phd
    phds = Group.objects.get(name="phds").user_set.all()
    for phd in phds:
        phd_to_add = dict()
        phd_to_add["id"] = phd.id
        phd_to_add["sciper"] = phd.sciper
        phd_to_add["first_name"] = phd.first_name
        phd_to_add["last_name"] = phd.last_name
        phds_info[phd.id] = phd_to_add
        phds_ids.append(phd.id)

    # Get the profile information about the phds
    if term == "HIVER":
        english_term = "winter"
    elif term == "ETE":
        english_term = "summer"
    else:
        pass

    availabilities = Availability.objects.filter(
        year=year, term=english_term, person_id__in=phds_ids
    ).all()
    for availability in availabilities:
        phds_info[availability.person_id]["availability"] = availability.availability

    # Add the missing information about the availabilities
    for phd in phds_info:
        if "availability" not in phds_info[phd]:
            phds_info[phd]["availability"] = ""

    # Get the courses ids in order to find the applications for them
    courses_ids_queryset = (
        Course.objects.filter(year=year, term=term).values("id").all()
    )
    courses_ids_list = list()
    [courses_ids_list.append(item["id"]) for item in courses_ids_queryset]

    # Retrieve all the applications for the PhD students for the current courses
    applications = Applications.objects.filter(
        course_id__in=courses_ids_list, applicant_id__in=phds_ids
    ).all()

    # Flag the PhDs with the correct information
    for application in applications:
        if application.status == "Pending":
            if "applications_pending" in phds_info[application.applicant_id]:
                phds_info[application.applicant_id]["applications_pending"] += 1
            else:
                phds_info[application.applicant_id]["applications_pending"] = 1
        elif application.status == "Hired":
            if "applications_accepted" in phds_info[application.applicant_id]:
                phds_info[application.applicant_id]["applications_accepted"] += 1
            else:
                phds_info[application.applicant_id]["applications_accepted"] = 1
        elif application.status == "Rejected":
            if "applications_declined" in phds_info[application.applicant_id]:
                phds_info[application.applicant_id]["applications_declined"] += 1
            else:
                phds_info[application.applicant_id]["applications_declined"] = 1
        elif application.status == "Withdrawn":
            if "applications_withdrawn" in phds_info[application.applicant_id]:
                phds_info[application.applicant_id]["applications_withdrawn"] += 1
            else:
                phds_info[application.applicant_id]["applications_withdrawn"] = 1

    # Add the missing information about the applications
    for phd in phds_info:
        if "applications_pending" not in phds_info[phd]:
            phds_info[phd]["applications_pending"] = ""
        if "applications_accepted" not in phds_info[phd]:
            phds_info[phd]["applications_accepted"] = ""
        if "applications_declined" not in phds_info[phd]:
            phds_info[phd]["applications_declined"] = ""
        if "applications_withdrawn" not in phds_info[phd]:
            phds_info[phd]["applications_withdrawn"] = ""

    context = {"year": year, "term": term, "phds": phds_info.values}

    return render(request, "web/reports/phds_list.html", context)


@is_staff()
def download_phds_report(request, year, term):
    phds_info = dict()
    phds_ids = list()

    # Get base information about the phd
    phds = Group.objects.get(name="phds").user_set.all()
    for phd in phds:
        phd_to_add = dict()
        phd_to_add["id"] = phd.id
        phd_to_add["sciper"] = phd.sciper
        phd_to_add["first_name"] = phd.first_name
        phd_to_add["last_name"] = phd.last_name
        phd_to_add["email"] = phd.email
        phds_info[phd.id] = phd_to_add
        phds_ids.append(phd.id)

    # Get the profile information about the phds
    if term == "HIVER":
        english_term = "winter"
    elif term == "ETE":
        english_term = "summer"
    else:
        pass

    availabilities = Availability.objects.filter(
        year=year, term=english_term, person_id__in=phds_ids
    ).all()
    for availability in availabilities:
        phds_info[availability.person_id]["availability"] = availability.availability

    # Add the missing information about the availabilities
    for phd in phds_info:
        if "availability" not in phds_info[phd]:
            phds_info[phd]["availability"] = ""

    # Get the courses ids in order to find the applications for them
    courses_ids_queryset = (
        Course.objects.filter(year=year, term=term).values("id").all()
    )
    courses_ids_list = list()
    [courses_ids_list.append(item["id"]) for item in courses_ids_queryset]

    # Retrieve all the applications for the PhD students for the current courses
    applications = Applications.objects.filter(
        course_id__in=courses_ids_list, applicant_id__in=phds_ids
    ).all()

    # Flag the PhDs with the correct information
    for application in applications:
        if application.status == "Pending":
            if "applications_pending" in phds_info[application.applicant_id]:
                phds_info[application.applicant_id]["applications_pending"] += 1
            else:
                phds_info[application.applicant_id]["applications_pending"] = 1
        elif application.status == "Hired":
            if "applications_accepted" in phds_info[application.applicant_id]:
                phds_info[application.applicant_id]["applications_accepted"] += 1
            else:
                phds_info[application.applicant_id]["applications_accepted"] = 1
        elif application.status == "Rejected":
            if "applications_declined" in phds_info[application.applicant_id]:
                phds_info[application.applicant_id]["applications_declined"] += 1
            else:
                phds_info[application.applicant_id]["applications_declined"] = 1
        elif application.status == "Withdrawn":
            if "applications_withdrawn" in phds_info[application.applicant_id]:
                phds_info[application.applicant_id]["applications_withdrawn"] += 1
            else:
                phds_info[application.applicant_id]["applications_withdrawn"] = 1

    # Add the missing information about the applications
    for phd in phds_info:
        if "applications_pending" not in phds_info[phd]:
            phds_info[phd]["applications_pending"] = ""
        if "applications_accepted" not in phds_info[phd]:
            phds_info[phd]["applications_accepted"] = ""
        if "applications_declined" not in phds_info[phd]:
            phds_info[phd]["applications_declined"] = ""
        if "applications_withdrawn" not in phds_info[phd]:
            phds_info[phd]["applications_withdrawn"] = ""

    # Time to build the excel file
    # content-type of response
    response = HttpResponse(content_type="application/ms-excel")

    # decide file name
    response[
        "Content-Disposition"
    ] = 'attachment; filename="phds_report_{year}_{term}.xls"'.format(
        year=year, term=term
    )

    # creating workbook
    wb = xlwt.Workbook(encoding="utf-8")

    # adding sheet
    ws = wb.add_sheet("sheet1")

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True

    # column header names, you can use your own headers here
    columns = [
        "sciper",
        "first name",
        "last name",
        "email",
        "availability",
        "pending applications",
        "accepted applications",
        "declined applications",
        "withdrawn applications",
    ]

    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    for key, phd in phds_info.items():
        row_num = row_num + 1
        ws.write(row_num, 0, phd["sciper"], font_style)
        ws.write(row_num, 1, phd["first_name"], font_style)
        ws.write(row_num, 2, phd["last_name"], font_style)
        ws.write(row_num, 3, phd["email"], font_style)
        ws.write(row_num, 4, phd["availability"], font_style)
        ws.write(row_num, 5, phd["applications_pending"], font_style)
        ws.write(row_num, 6, phd["applications_accepted"], font_style)
        ws.write(row_num, 7, phd["applications_declined"], font_style)
        ws.write(row_num, 8, phd["applications_withdrawn"], font_style)
    wb.save(response)
    return response


@is_staff()
def phds_profiles(request):
    year = config.get_config("current_year")
    term = config.get_config("current_term")
    if term == "HIVER":
        term = "winter"
    elif term == "ETE":
        term = "summer"
    else:
        pass

    students_infos = dict()
    students_ids = list()

    # get the base info about the students
    students = Group.objects.get(name="phds").user_set.all()
    for student in students:
        student_to_add = dict()
        student_to_add["id"] = student.id
        student_to_add["sciper"] = student.sciper
        student_to_add["first_name"] = student.first_name
        student_to_add["last_name"] = student.last_name
        student_to_add["english"] = student.canTeachInEnglish
        student_to_add["french"] = student.canTeachInFrench
        student_to_add["german"] = student.canTeachInGerman
        students_infos[student.id] = student_to_add
        students_ids.append(student.id)

    # Get the profile information about the phds
    availabilities = Availability.objects.filter(
        year=year, term=term, person_id__in=students_ids
    ).all()
    for availability in availabilities:
        students_infos[availability.person_id][
            "availability"
        ] = availability.availability
        students_infos[availability.person_id][
            "availability_reason"
        ] = availability.reason

    # Add the missing information about the availabilities
    for student in students_infos:
        if "availability" not in students_infos[student]:
            students_infos[student]["availability"] = ""
            students_infos[student]["availability_reason"] = ""

    # time to render the template
    context = {"students": students_infos.values}
    return render(request, "web/reports/students_profiles.html", context=context)


@is_staff()
def applications_list(request):
    year = config.get_config("current_year")
    term = config.get_config("current_term")

    courses = Course.objects.filter(year=year, term=term).all()
    applications = (
        Applications.objects.filter(course__in=courses)
        .prefetch_related("course", "applicant")
        .all()
    )

    context = {
        "applications": applications,
    }
    return render(request, "web/reports/applications_list.html", context)


@is_staff()
def delete_application(request, application_id):
    application = get_object_or_404(Applications, id=application_id)
    application.delete()
    messages.success(request, "The application was successfully deleted")
    return HttpResponseRedirect(reverse("web:applications_list"))


@is_staff()
def batch_upload_phds(request):
    context = {}
    return render(request, "web/forms/students/batchupload.html", context)


def load_emails(emails):
    return_value = []

    for email in emails:
        # The email address might contain multiple email addresses on the same line (e.g. emmanuel.jaep@epfl.ch,emmanuel.jaep@gmail.com).
        # We need to keep only the one at EPFL
        subemails = email.split(",")
        if len(subemails) > 1:
            for subemail in subemails:
                if "@epfl.ch" in subemail:
                    email = subemail

        user_exists = False

        try:
            db_user = Person.objects.get(email__iexact=email)
            return_value.append(
                {"email": email, "level": "info", "msg": "The user already exists"}
            )
            user_exists = True
        except ObjectDoesNotExist:
            person = epfl_ldap.get_user_by_email(settings, email)
            if type(person) != type(dict()):
                return_value.append(
                    {
                        "email": email,
                        "level": "warning",
                        "msg": "User not found in LDAP",
                    }
                )
            else:
                # We may have a user existing in the database without the email address but with the same username
                username = person["username"]
                sciper = person["sciper"]

                user_exists_with_same_username = False
                try:
                    user_with_same_username = Person.objects.get(
                        username__iexact=username
                    )
                    user_exists_with_same_username = True
                except ObjectDoesNotExist:
                    pass

                user_exists_with_same_sciper = False
                try:
                    user_with_same_sciper = Person.objects.get(sciper=sciper)
                    user_exists_with_same_sciper = True
                except ObjectDoesNotExist:
                    pass

                if (
                    user_exists_with_same_sciper == False
                    and user_exists_with_same_username == False
                ):  # if we are sure that the user does not exist in the db
                    db_user = Person()
                    db_user.sciper = person["sciper"]
                    db_user.username = person["username"]
                    db_user.email = person["mail"]
                    db_user.first_name = person["first_name"]
                    db_user.last_name = person["last_name"]
                    db_user.save()
                    return_value.append(
                        {
                            "email": email,
                            "level": "success",
                            "msg": "User successfully added",
                        }
                    )
                    user_exists = True
                else:
                    if user_exists_with_same_username == True:
                        db_user = user_with_same_username
                        user_exists = True
                    elif user_exists_with_same_sciper == True:
                        db_user = user_with_same_sciper
                        user_exists = True

        # time to deal with the group membership
        if user_exists:
            try:
                group = Group.objects.get(name="phds")
            except ObjectDoesNotExist:
                group = Group()
                group.name = "phds"
                group.save()

            if db_user not in group.user_set.all():
                group.user_set.add(db_user)
                db_user.save()
                group.save()
                return_value.append(
                    {
                        "email": email,
                        "level": "success",
                        "msg": "user successfully added to group",
                    }
                )

    return return_value


@is_staff()
def batch_upload_phds_ajax(request):
    if request.is_ajax():
        emails = request.POST.get("emails", None)
        if emails:
            emails = emails.split("\n")
            details = load_emails(emails)
            response = {"msg": "Your form has been submitted", "details": details}
            return JsonResponse(response)


@is_staff_or_teacher()
def add_phd(request):
    add_phd_form = PeopleManagementForm(request.POST or None)

    if request.method == "POST":
        if add_phd_form.is_valid():
            # extract the sciper from the passed value
            pattern = r".*,\s.*\((\d*)\)"
            if not re.match(pattern, add_phd_form.cleaned_data["add_person"]):
                messages.error(request, "Unable to find the sciper in the passed value")
            else:
                sciper = re.match(pattern, add_phd_form.cleaned_data["add_person"])[1]
                # try to find the person in LDAP
                person = epfl_ldap.get_user_by_username_or_sciper(settings, sciper)

                if type(person) == type(dict()):
                    # Check if the person is already in the database
                    try:
                        db_user = Person.objects.get(sciper=person["sciper"])
                        messages.warning(
                            request, "The user already existed in the database"
                        )
                    except ObjectDoesNotExist:
                        db_user = Person()
                        db_user.sciper = person["sciper"]
                        db_user.username = person["username"]
                        db_user.email = person["mail"]
                        db_user.first_name = person["first_name"]
                        db_user.last_name = person["last_name"]
                        db_user.save()

                    # Check if the group already exists (create it if necessary)
                    try:
                        group = Group.objects.get(name="phds")
                    except ObjectDoesNotExist:
                        group = Group()
                        group.name = "phds"
                        group.save()

                    # phds = Group.objects.get(name="phds")
                    if db_user in group.user_set.all():
                        messages.warning(
                            request, "The user was already part of the group"
                        )
                    else:
                        group.user_set.add(db_user)
                        db_user.save()
                        group.save()
                        messages.success(
                            request, "The student has been successfully added"
                        )
                else:
                    messages.error(
                        request,
                        "Unable to find the person in the directory ({})".format(
                            person
                        ),
                    )

    context = {
        "form": add_phd_form,
    }
    return render(request, "web/add_phd_form.html", context)


@is_staff()
def autocomplete_phds(request):
    if request.is_ajax():
        q = request.GET.get("term", "").capitalize()
        results = epfl_ldap.get_users_by_partial_username_or_partial_sciper(settings, q)
        data = json.dumps(results)
    else:
        data = "fail"

    mimetype = "application/json"
    return HttpResponse(data, mimetype)


@is_staff()
def get_course_applications_details(request):
    if request.is_ajax():
        year = request.POST["year"]
        term = request.POST["term"]
        courseCode = request.POST["courseCode"]
        applicationType = request.POST["type"]

        course = Course.objects.get(year=year, term=term, code=courseCode)
        if applicationType == "received":
            applications = Applications.objects.filter(course=course).all()
        else:
            applications = Applications.objects.filter(
                course=course, status=applicationType
            ).all()

        return_value = ""
        for application in applications:
            person = application.applicant
            return_value += "{}, {}<a target='_blank' href='{}'><i style='margin-left: 5px;' class='fas fa-external-link-alt'></i></a><br/>".format(
                person.last_name,
                person.first_name,
                reverse("web:view_profile", args=(person.id,)),
            )
        mimetype = "text/html"
        return HttpResponse(return_value, mimetype)

    else:
        data: "fail"
        mimetype = "application/json"
        return HttpResponse(data, mimetype)


@is_staff_or_teacher()
def autocomplete_phds_from_person(request):
    if request.is_ajax():
        q = request.GET.get("term", "")
        if re.match(r"^\d*$", q):
            # get all the phds having that sciper
            phds = Group.objects.get(name="phds").user_set.filter(sciper=q).all()

            # get all the aes having that sciper
            aes = Group.objects.get(name="aes").user_set.filter(sciper=q).all()

            # merge the 2 querysets
            persons = (phds | aes).distinct()
        else:
            # get all the phds having a partial matching name
            phds = (
                Group.objects.get(name="phds")
                .user_set.filter(Q(last_name__icontains=q) | Q(first_name__icontains=q))
                .all()
            )

            # get all the aes having a partial matching name
            aes = (
                Group.objects.get(name="aes")
                .user_set.filter(Q(last_name__icontains=q) | Q(first_name__icontains=q))
                .all()
            )

            # merge the 2 querysets
            persons = (phds | aes).distinct()

        # Build the list to be displayed on the page
        return_value = list()
        [
            return_value.append(
                "{}, {} ({})".format(person.last_name, person.first_name, person.sciper)
            )
            for person in persons
        ]

        return_value = json.dumps(return_value)
    else:
        return_value = "fail"

    mimetype = "application/json"
    return HttpResponse(return_value, mimetype)


@is_staff_or_teacher()
def autocomplete_courses(request):
    if request.is_ajax():
        year = config.get_config("current_year")
        term = config.get_config("current_term")
        q = request.GET.get("term", "")

        # get the list of courses
        # if the requester is staff, all the courses matching the query will get displayed
        # if the requester is 'simply' a teacher, only the courses belonging to that person will get displayed
        if request.user.is_staff:
            courses = Course.objects.filter(
                Q(code__icontains=q) | Q(subject__icontains=q), year=year, term=term
            ).all()
        elif request.user.groups.filter(name="teachers").exists():
            # get all the Teachings of that person
            teachings = (
                Teaching.objects.filter(person=request.user)
                .select_related("course")
                .all()
            )

            # extract the ids of the courses in order to use them downlstream
            courses_ids = []
            [courses_ids.append(teaching.course.id) for teaching in teachings]

            # get all the courses of that person meeting the partial name or code
            courses = Course.objects.filter(
                Q(code__icontains=q) | Q(subject__icontains=q),
                year=year,
                term=term,
                id__in=courses_ids,
            ).all()
        else:
            raise PermissionDenied()

        return_value = list()
        [
            return_value.append("{} ({})".format(course.subject, course.code))
            for course in courses
        ]
        return_value = json.dumps(return_value)
    else:
        return_value = "fail"

    mimetype = "application/json"
    return HttpResponse(return_value, mimetype)


@is_staff_or_teacher()
def add_assignment(request):
    add_assignment_form = AssignmentManagementForm(request.POST or None)

    if request.method == "POST":
        if add_assignment_form.is_valid():

            # time to extract the information from the form
            sciper_pattern = r"^.*\s\((\d*)\)$"
            sciper = re.match(
                sciper_pattern, add_assignment_form.cleaned_data["person"]
            ).group(1)
            try:
                applicant = Person.objects.get(sciper=sciper)
            except ObjectDoesNotExist:
                applicant = None
                messages.error(request, "The user was not found in the database")

            course_pattern = r"^(.*)\s\((.*)\)$"
            subject = re.match(
                course_pattern, add_assignment_form.cleaned_data["course"]
            ).group(1)
            code = re.match(
                course_pattern, add_assignment_form.cleaned_data["course"]
            ).group(2)
            year = config.get_config("current_year")
            term = config.get_config("current_term")
            try:
                course = Course.objects.get(
                    subject=subject, code=code, year=year, term=term
                )
            except ObjectDoesNotExist:
                course = None
                messages.error(request, "The course was not found in the database")

            if applicant and course:
                # first, we have to check if the user is allowed to save this application
                # i.e. if the user is staff, any course can be selected
                #      if the user is a teacher, then he can only select a course he is teaching
                if request.user.is_staff:
                    # no need to process further
                    pass
                elif request.user.groups.filter(name="teachers").exists():
                    # get all the Teachings of that person
                    teachings = (
                        Teaching.objects.filter(person=request.user)
                        .select_related("course")
                        .all()
                    )

                    # extract the ids of the courses in order to use them downlstream
                    courses_ids = []
                    [courses_ids.append(teaching.course.id) for teaching in teachings]
                    if course.id not in courses_ids:
                        raise PermissionDenied()
                else:
                    raise PermissionDenied()
                try:
                    application = Applications.objects.get(
                        course=course, applicant=applicant
                    )
                except ObjectDoesNotExist:
                    application = Applications()

                application.course = course
                application.applicant = applicant
                # application.role = add_assignment_form.cleaned_data['role']
                application.status = "Hired"
                application.closedAt = now()
                application.closedBy = request.user
                application.source = "web"
                application.decisionReason = "TA duty assigned by section or teacher"
                application.save()
                messages.success(request, "Teaching duty successfully saved.")

    context = {"form": add_assignment_form}
    return render(request, "web/add_phd_assignment_form.html", context)


@is_staff()
def phds_with_multiple_hirings_report(request):
    year = config.get_config("current_year")
    term = config.get_config("current_term")

    all_courses = Course.objects.filter(year=year, term=term).all()
    courses_ids = [course.id for course in all_courses]

    all_applications = (
        Applications.objects.filter(course_id__in=courses_ids, status="Hired")
        .prefetch_related("applicant")
        .all()
    )

    context = {
        "hirings": all_applications,
    }

    return render(request, "web/reports/phds_with_multiple_hirings.html", context)


@is_staff()
def get_courses_without_numberOfTARequests(request):
    year = config.get_config("current_year")
    term = config.get_config("current_term")

    this_term_courses = Course.objects.filter(year=year, term=term).all()
    this_term_requests = (
        NumberOfTAUpdateRequest.objects.filter(course__year=year, course__term=term)
        .select_related("course")
        .all()
    )
    courses_with_requests_ids = list()
    [
        courses_with_requests_ids.append(TARequest.course.id)
        for TARequest in this_term_requests
    ]
    courses_without_requests = this_term_courses.exclude(
        id__in=courses_with_requests_ids
    ).prefetch_related("teachers")
    context = {"courses": courses_without_requests}

    return render(
        request, "web/reports/TARequests/courses_without_requests.html", context=context
    )

