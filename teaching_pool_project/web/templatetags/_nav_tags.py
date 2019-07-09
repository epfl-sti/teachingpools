from django import template
from django.utils.html import mark_safe

register = template.Library()


@register.filter(name="get_badge")
def is_staff(user):
    if user.is_superuser:
        badge_icon = 'fa-user-ninja'
    elif user.is_staff:
        badge_icon = 'fa-user-shield'
    elif user.groups.filter(name='teachers').exists():
        badge_icon = 'fa-user-tie'
    elif user.groups.filter(name='phds').exists():
        badge_icon = 'fa-user-graduate'
    else:
        badge_icon = 'fa-user'

    return_value = "{first}. {last}&nbsp;<i class='fas {icon}'></i>".format(
        first=user.first_name[:1],
        last=user.last_name,
        icon=badge_icon
    )

    return mark_safe(return_value)
