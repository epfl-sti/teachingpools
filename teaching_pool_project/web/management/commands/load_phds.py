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
            try:
                person_obj = Person.objects.get(sciper=phd['sciper'])
            except ObjectDoesNotExist:
                person_obj= Person()
                person_obj.sciper = phd['sciper']
                person_obj.save()

            try:
                person_obj.username = phd['username']
                person_obj.save()
            except Exception as ex:
                print("{} - unable to save username".format(phd['sciper']))
                raise ex

            try:
                person_obj.email = phd['email']
                person_obj.save()
            except Exception as ex:
                print("{} - unable to save email".format(phd['sciper']))
                raise ex

            try:
                person_obj.first_name = phd['first_name'][:30]
                person_obj.save()
            except Exception as ex:
                print("{} - unable to save first_name".format(phd['sciper']))
                raise ex

            try:
                person_obj.last_name = phd['last_name']
                person_obj.save()
            except Exception as ex:
                print("{} - unable to save last_name".format(phd['sciper']))
                raise ex

            try:
                person_obj.role = 'teaching assistant'
                person_obj.save()
            except Exception as ex:
                print("{} - unable to save role".format(phd['sciper']))
                raise ex

            phd_group.user_set.add(person_obj)
