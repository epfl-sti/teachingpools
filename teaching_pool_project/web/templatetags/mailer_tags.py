from django import template
from django.conf import settings
from django.utils.html import mark_safe
from django.utils.text import slugify
from django.urls import reverse

from web.models import *

register = template.Library()


@register.filter(name="get_campaign_row_class")
def get_campaign_row_class(campaign):
    if campaign.status == "pending":
        return "table-secondary"
    elif campaign.status == "in progress":
        return "table-primary"
    elif campaign.status == "successfully finished":
        return "table-success"
    elif campaign.status == "finished with errors":
        return "table-danger"
    else:
        return ""


@register.filter(name="get_campaign_status_icon")
def get_campaign_status_icon(campaign):
    if campaign.status == "pending":
        return "<i class='far fa-hourglass'></i>"
    elif campaign.status == "in progress":
        return '<i class="fas fa-cog"></i>'
    elif campaign.status == "successfully finished":
        return '<i class="fas fa-check"></i>'
    elif campaign.status == "finished with errors":
        return '<i class="fas fa-bug"></i>'
    else:
        return ""


@register.filter(name="get_email_row_class")
def get_email_row_class(email):
    if email.status == "pending":
        return "table-secondary"
    elif email.status == "sent":
        return "table-success"
    elif email.status == "error":
        return "table-danger"
    else:
        return ""


@register.filter(name="get_email_status_icon")
def get_email_status_icon(email):
    if email.status == "pending":
        return "<i class='far fa-hourglass'></i>"
    elif email.status == "sent":
        return '<i class="fas fa-check"></i>'
    elif email.status == "error":
        return '<i class="fas fa-bug"></i>'
    else:
        return ""
