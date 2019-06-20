# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.conf import settings
from django.views import generic
from django.db.models import Prefetch
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.utils.timezone import now

from .forms import NameForm, RequestForTA, RequestForTAApproval, RequestForTAView
from .models import Course, Teaching, NumberOfTAUpdateRequest, Person
from epfl.sti.helpers import ldap as epfl_ldap


def get_impersonated_user(request):
    if request.COOKIES.get('impersonate', '') != '' and settings.DEBUG:
        return request.COOKIES.get('impersonate', '')
    else:
        return request.user.username


def notify_admins_and_requester(data, template_base, admins_subject, requesters_subject, admins, requesters):
    admins_subject = settings.EMAIL_SUBJECT_PREFIX + admins_subject
    admins_template = '{}_admins'.format(template_base)
    admins_sender = settings.EMAIL_FROM
    admin_recipients = settings.EMAIL_ADMINS
    notify_people(data=data, template=admins_template, subject=admins_subject,
                  sender=admins_sender, recipients=admin_recipients)

    requester_subject = settings.EMAIL_SUBJECT_PREFIX + requesters_subject
    requester_template = '{}_requester'.format(template_base)
    requester_sender = settings.EMAIL_FROM
    requester_recipients = requesters
    notify_people(data=data, template=requester_template, subject=requester_subject,
                  sender=requester_sender, recipients=requester_recipients)


def notify_people(data={}, template='', subject='', sender='', recipients=list()):
    mail_subject = settings.EMAIL_SUBJECT_PREFIX + subject
    plaintext = get_template('web/emails/{}.txt'.format(template))
    htmly = get_template('web/emails/{}.html'.format(template))
    text_content = plaintext.render(data)
    htmly_content = htmly.render(data)
    msg = EmailMultiAlternatives(
        subject=mail_subject,
        body=text_content,
        from_email=sender,
        to=recipients)
    msg.attach_alternative(htmly_content, "text/html")
    msg.send()


def index(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    return render(request, 'web/index.html')


def courses_full_list(request, year):
    all_courses = Course.objects.filter(
        year=year).prefetch_related('teachers').all()
    context = {
        'courses': all_courses
    }
    return render(request, 'web/all_courses.html', context)


def courses_list_year_teacher(request, year):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    username = get_impersonated_user(request)
    sciper = epfl_ldap.get_sciper(settings, username)

    teachings = Teaching.objects.filter(
        person=sciper).prefetch_related('course').all()

    context = {
        'teachings': teachings
    }
    return render(request, 'web/prof_courses.html', context)

def requests_for_tas_teacher(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    username = get_impersonated_user(request)
    sciper = epfl_ldap.get_sciper(settings, username)

    requests = NumberOfTAUpdateRequest.objects.filter(requester=sciper).prefetch_related('course').order_by('openedAt').all()
    context = {
        'requests': requests
    }
    return render(request, 'web/prof_ta_requests.html', context)

def requests_for_tas_teacher_status(request, status):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    username = get_impersonated_user(request)
    sciper = epfl_ldap.get_sciper(settings, username)

    requests = NumberOfTAUpdateRequest.objects.filter(requester=sciper, status=status.capitalize()).prefetch_related('course').order_by('openedAt').all()
    context = {
        'requests': requests
    }
    return render(request, 'web/prof_ta_requests.html', context)

def request_for_TA(request, course_id):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    username = get_impersonated_user(request)
    sciper = epfl_ldap.get_sciper(settings, username)
    mail = epfl_ldap.get_mail(settings, username)

    if request.method == 'POST':
        form = RequestForTA(request.POST)
        if form.is_valid():

            requester = Person.objects.get(sciper=sciper)
            course = Course.objects.get(pk=form.cleaned_data['course_id'])

            request_obj = NumberOfTAUpdateRequest()
            request_obj.requester = requester
            request_obj.course = course
            request_obj.requestedNumberOfTAs = form.cleaned_data['number_of_TAs']
            request_obj.requestReason = form.cleaned_data['reason']
            request_obj.save()
            request_obj.course.requestedNumberOfTAs = request_obj.requestedNumberOfTAs
            request_obj.course.save()
            request_id = request_obj.pk

            data = {'request': request_obj}
            requesters = list()
            requesters.append(mail)

            notify_admins_and_requester(
                data=data,
                template_base='new_ta_request',
                admins_subject='A new TA request has been recorded',
                requesters_subject='Your request for TA has been recorded',
                admins=settings.EMAIL_ADMINS,
                requesters=requesters)

            return HttpResponseRedirect(reverse('web:courses_list_year_teacher', args=['2019-2020']))
    else:
        course = Course.objects.get(pk=course_id)
        form = RequestForTA()
        form.fields['course_id'].initial = course_id
        context = {
            'course_id': course_id,
            'course': course,
            'form': form
        }
        return render(request, 'web/request_for_ta_form.html', context)


def get_TAs_requests_to_validate(request):
    requests = NumberOfTAUpdateRequest.objects.filter(status='Pending').all()
    context = {
        'requests': requests
    }
    return render(request, 'web/requests_for_tas.html', context)


def validate_request_for_TA(request, request_id):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    username = get_impersonated_user(request)
    sciper = epfl_ldap.get_sciper(settings, username)

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
            person = Person.objects.get(pk=sciper)
            request_obj.decidedBy = person
            if status == "Approved":
                request_obj.course.approvedNumberOfTAs = request_obj.requestedNumberOfTAs
                request_obj.course.save()
            request_obj.save()

            # Notification
            notification_recipients = list()
            notification_recipients.append(request_obj.requester.email)
            notify_people(
                data={'request': request_obj},
                template="ta_request_approval",
                subject="Your request for TA has been {}".format(
                    status.lower()),
                sender=settings.EMAIL_FROM,
                recipients=notification_recipients)

            return HttpResponseRedirect(reverse('web:get_TAs_requests_to_validate'))

    else:
        requestForTA = NumberOfTAUpdateRequest.objects.get(pk=request_id)
        form = RequestForTAApproval()
        form.fields['request_id'].initial = requestForTA.pk
        form.fields['opened_at'].initial = requestForTA.openedAt
        form.fields['requester'].initial = "{}, {}".format(
            requestForTA.requester.lastName, requestForTA.requester.firstName)
        form.fields['course'].initial = "{} ({})".format(
            requestForTA.course.subject, requestForTA.course.code)
        form.fields['requestedNumberOfTAs'].initial = requestForTA.requestedNumberOfTAs
        form.fields['reason_for_request'].initial = requestForTA.requestReason

        context = {
            'request_id': request_id,
            'form': form
        }
        return render(request, 'web/request_for_ta_review_form.html', context)

def view_request_for_TA(request, request_id):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    username = get_impersonated_user(request)

    ta_request = NumberOfTAUpdateRequest.objects.get(pk=request_id)
    form = RequestForTAView()
    form.fields['request_id'].initial = ta_request.pk
    form.fields['opened_at'].initial = ta_request.openedAt
    form.fields['requester'].initial = "{}, {}".format(
            ta_request.requester.lastName, ta_request.requester.firstName)
    form.fields['course'].initial = "{} ({})".format(
            ta_request.course.subject, ta_request.course.code)
    form.fields['requestedNumberOfTAs'].initial = ta_request.requestedNumberOfTAs
    form.fields['reason_for_request'].initial = ta_request.requestReason
    form.fields['reason_for_decision'].initial = ta_request.decisionReason

    context = {
        'request_id': request_id,
        'form': form
    }

    return render(request, 'web/request_for_ta_view_form.html', context)
