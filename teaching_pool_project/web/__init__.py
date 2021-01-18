import logging

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

logger = logging.getLogger(__name__)

default_app_config = "web.apps.WebConfig"


@receiver(user_logged_in)
def on_login(sender, user, request, **kwargs):
    logger.info("checking if the user is a TA")
    try:
        if user.group:
            if "STI_TA_Students" in user.group:
                if user.is_active is False:
                    logger.debug("re-enabling account")
                    user.is_active = True
                    user.save()

                from django.contrib.auth.models import Group

                logger.debug("yes")
                phd_group = Group.objects.get(name="phds")
                user.groups.add(phd_group)
            else:
                from django.contrib.auth.models import Group

                logger.debug("no")
                phd_group = Group.objects.get(name="phds")
                user.groups.remove(phd_group)
        else:
            logger.debug("groups not imported from Tequila")
    except:
        logger.exception("unable to check if the user is a TA")
