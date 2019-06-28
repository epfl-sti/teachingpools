from django import template
from django.conf import settings
from django.utils.html import mark_safe
from django.urls import reverse

from web.models import *

register = template.Library()


@register.filter(name="format_teachers")
def format_teachers(course):
    teachers = list()
    for teacher in course.teachers.all():
        teachers.append("{}. {}".format(
            teacher.first_name[:1], teacher.last_name))
    return ", ".join(teachers)


@register.filter(name="format_languages")
def format_languages(course):
    languages = list()
    if course.taughtInFrench:
        languages.append("French")
    if course.taughtInEnglish:
        languages.append("English")
    if course.taughtInGerman:
        languages.append("German")
    return ", ".join(languages)


@register.filter(name="format_forms")
def format_forms(course):
    forms = list()
    if course.has_course:
        forms.append('Course')
    if course.has_exercises:
        forms.append('Exercises')
    if course.has_project:
        forms.append('Project')
    if course.has_practical_work:
        forms.append('Practical work')
    return ", ".join(forms)


@register.simple_tag
def get_badge(course, user, courses_applied_to):
    return_value = ''

    # check if the current user is actually teaching this course
    if user in course.teachers.all():

        # builds up a pill to give him a link to his courses
        pill = '&nbsp;<a  href="{}" class="badge badge-pill badge-info">You</a>'.format(reverse('web:courses_list_year_teacher', args=[settings.APP_CURRENT_YEAR]))
        return_value += pill

        # Check if there are pending requests for TAs
        has_pending_requests = NumberOfTAUpdateRequest.objects.filter(requester=user, course=course, status="Pending").exists()
        if has_pending_requests:

            # Build a link to the pending TA requests
            pill = '&nbsp;<a  href="{}" class="badge badge-pill badge-info">Pending requests</a>'.format(reverse('web:requests_for_tas_teacher_status', args=['Pending']))
            return_value += pill

    if course.pk in courses_applied_to:
        pill = '&nbsp;<a  href="{}" class="badge badge-pill badge-info">applied</a>'.format(reverse('web:requests_for_tas_teacher_status', args=['Pending']))
        return_value += pill

    return mark_safe(return_value)


@register.simple_tag
def get_apply_button(course, user):
    return_value = ''
    return_value = '<a href="{}" class="btn btn-primary">Apply</a>'.format(reverse('web:apply', args=[course.pk]))

    return mark_safe(return_value)
