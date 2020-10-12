import logging

from django.conf import settings
from django.contrib.auth.models import Group
from epfl.sti.helpers import ldap as epfl_ldap
from web.models import Person

logger = logging.getLogger(__name__)


def synchronize_people():
    logger.info("synchronizing local DB with LDAP")

    deactivate_old_phds()
    get_new_phds()

    logger.info("finished synchronizing with LDAP group")


def get_new_phds():
    logger.info("Retrieving all TAs from LDAP")
    phd_group = Group.objects.get(name="phds")

    TAs = epfl_ldap.get_STI_TA_Students(settings)
    for key, TA in TAs.items():
        try:
            TA_obj = Person.objects.get(sciper=TA["sciper"])
            logger.debug("found entry for sciper {}".format(TA["sciper"]))
        except Person.DoesNotExist:
            logger.info("creating user for sciper {}".format(TA["sciper"]))
            TA_obj = Person()

        TA_obj.sciper = TA["sciper"]
        TA_obj.username = TA["username"]
        TA_obj.first_name = TA["first_name"]
        TA_obj.last_name = TA["last_name"]
        TA_obj.email = TA["mail"]
        TA_obj.save()

        TA_obj.groups.add(phd_group)


def deactivate_old_phds():
    logger.info("Deactivating PhDs who are not part of the STI_TA_Students anymore")

    logger.debug("getting phd group")
    phds_group = Group.objects.get(name="phds")

    logger.debug("getting list of active phds scipers")
    active_phds = list(
        phds_group.user_set.filter(is_active=True).values_list("sciper", flat=True)
    )

    logger.debug("getting the status of these scipers in LDAP")
    statuses = epfl_ldap.get_phds_status_by_scipers(settings, active_phds)

    logger.debug("checking consistency")
    for sciper in active_phds:
        logger.debug("checking sciper {}".format(sciper))
        status = statuses[sciper]

        if status == False:
            logger.debug("deactivating account")
            user = Person.objects.get(sciper=sciper)
            user.is_active = False
            user.save()

            logger.debug("remove from phd group")
            user.groups.remove(phds_group)

