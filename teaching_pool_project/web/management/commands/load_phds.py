import io
from math import ceil
import os.path
import pickle

import numpy
import pandas as pd
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from epfl.sti.helpers import ldap as epfl_ldap
from web.models import Course, Person, Teaching


class Command(BaseCommand):
    def handle(self, **options):
        # Load the list of PhDs scipers
        with open(settings.LIST_OF_PHD_SCIPERS,'r') as file:
            scipers = file.readlines()
            scipers = [sciper.strip() for sciper in scipers]

        data_to_load = epfl_ldap.get_users(settings, scipers)

        phd_group = Group.objects.get(name="phds")

        for phd in data_to_load:
            person_obj, created = Person.objects.get_or_create(sciper = phd['sciper'])
            if created:
                person_obj.username = phd['username']
                person_obj.email = phd['email']
                person_obj.first_name = phd['first_name']
                person_obj.last_name = phd['last_name']
                person_obj.role = 'teaching assistant'
                person_obj.save()

            phd_group.user_set.add(person_obj)
