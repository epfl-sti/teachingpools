from django import template

register = template.Library()


@register.filter(name="is_superuser")
def is_staff(user):
    return user.is_superuser


@register.filter(name="is_staff")
def is_staff(user):
    return user.is_staff


@register.filter(name="is_teacher")
def is_teacher(user):
    return user.groups.filter(name='teachers').exists()


@register.filter(name="is_staff_or_teacher")
def is_staff_or_teacher(user):
    return (is_staff(user) or is_teacher(user))


@register.filter(name="is_phd")
def is_phd(user):
    return user.groups.filter(name='phds').exists()


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter(name='get_status_class')
def get_class_from_status(status):
    status = status.lower()
    if status == "approved":
        return "badge-pill badge-success"
    elif status == "pending":
        return "badge-pill badge-info"
    elif status == "declined":
        return "badge-pill badge-danger"
    else:
        return ""
