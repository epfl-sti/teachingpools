from django import template
from django.urls import reverse
from django.utils.html import mark_safe

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
