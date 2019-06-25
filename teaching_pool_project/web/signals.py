from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.auth.models import Group
from epfl.sti.helpers import ldap as epfl_ldap
from web.models import Person

@receiver(user_logged_in)
def check_if_user_is_phd(sender, request, **kwargs):
    if epfl_ldap.is_phd(settings, request.user.sciper):
        if not request.user.groups.filter(name="phds").exists():
            phd_group = Group.objects.get(name="phds")
            phd_group.user_set.add(request.user)
    else:
        if request.user.groups.filter(name="phds").exists():
            phd_group = Group.objects.get(name="phds")
            phd_group.user_set.remove(request.user)
