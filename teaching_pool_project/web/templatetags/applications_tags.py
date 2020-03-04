from django import template
from django.urls import reverse
from django.utils.html import mark_safe

from web.models import Person, Course, Applications

register = template.Library()


@register.simple_tag
def get_badge(application):
    return_value = ''

    if application.status == 'Pending':
        return_value = '&nbsp;<span class="badge badge-pill badge-info">pending</span>'
    if application.status == 'Hired':
        return_value = '&nbsp;<span class="badge badge-pill badge-success">accepted</span>'
    if application.status == 'Rejected':
        return_value = '&nbsp;<span class="badge badge-pill badge-danger">rejected</span>'
    if application.status == 'Withdrawn':
        return_value = '&nbsp;<span class="badge badge-pill badge-secondary">withdrawn</span>'

    return mark_safe(return_value)


@register.simple_tag
def get_application_section(application):
    return_value = ''
    teachers = application.course.person_set.all()
    for teacher in teachers:
        if teacher.section:
            return_value = teacher.section.name
            break
    return return_value


@register.simple_tag
def get_application_course_teachers(application):
    # return_value = '<ul>'
    return_value = ''
    teachers = application.course.person_set.all()
    for teacher in teachers:
        # return_value += "<li>{}, {}</li>".format(teacher.last_name, teacher.first_name)
        return_value += "{}, {}<br/>".format(teacher.last_name, teacher.first_name)
    # return_value += "</ul>"
    return_value += ""
    return mark_safe(return_value)

@register.filter
def has_applications(course):
    return Applications.objects.filter(course=course).count() > 0

@register.filter
def has_accepted_applications(course):
    return Applications.objects.filter(course=course, status='Hired').count() > 0

@register.filter
def has_rejected_applications(course):
    return Applications.objects.filter(course=course, status='Rejected').count() > 0

@register.filter
def has_withdrawn_applications(course):
    return Applications.objects.filter(course=course, status='Withdrawn').count() > 0
