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
        # Load the courses for the current year
        df = pd.read_excel(settings.EXCEL_FILE_TO_LOAD)
        for index, row in df.iterrows():
            course_code = row['code']
            subject = row['subject']
            if type(row['teachers']) != type(float()):
                raw_teachers = [x.strip() for x in row['teachers'].split(';')]
            else:
                raw_teachers = list()
            term = row['term']
            if type(row['type']) != type(float()):
                raw_types = [x.strip() for x in row['type'].split(',')]
            else:
                raw_types = list()

            if numpy.isnan(row['students']):
                row['students'] = numpy.nan_to_num(row['students'])
            students = int(row['students'])

            if type(row['languages']) != type(float()):
                raw_languages = [x.strip()
                                 for x in row['languages'].split('/')]
            else:
                raw_languages = list()

            teachers = load_teachers(raw_teachers)
            load_course(settings.EXCEL_LOADER_CURRENT_YEAR, term, course_code,
                        subject, raw_types, teachers, students, raw_languages)

        # Now time to load the stats for the previous year
        df = pd.read_excel(settings.EXCEL_FILE_TO_LOAD_FOR_PREVIOUS_YEAR)
        for index, row in df.iterrows():
            course_code = row['code']
            term = row['term']
            if numpy.isnan(row['students']):
                row['students'] = numpy.nan_to_num(row['students'])
            students = int(row['students'])
            update_course(settings.EXCEL_LOADER_CURRENT_YEAR,
                          term, course_code, students)


def update_course(year, term, code, students):
    try:
        course = Course.objects.get(year=year, term=term, code=code)
        course.numberOfStudents = students
        if course.has_exercises or course.has_practical_work:
            course.calculatedNumberOfTAs = int(ceil((students/25)))
        course.save()
    except ObjectDoesNotExist:
        print("Course not found in '{year}' -> term:{term}, code:{code}".format(
            year=year, term=term, code=code))


def load_teachers(teachers=list()):
    # Sanity check to make sure that the required groups are present
    check_groups_are_present()
    teachers_group = Group.objects.get(name="teachers")

    return_value = list()

    if not os.path.isfile(settings.PICKLED_DATA_FROM_LDAP):
        load_mappings()

    pickle_in = open(
        settings.PICKLED_DATA_FROM_LDAP, 'rb')
    mappings = pickle.load(pickle_in)

    for teacher in teachers:
        if teacher in mappings:
            base_data = mappings[teacher]
            try:
                existing_user = Person.objects.get(sciper=base_data['sciper'])

                # Make sure that the teacher belongs to the teachers group
                if not existing_user.groups.filter(name="teachers").exists():
                    teachers_group.user_set.add(existing_user)

                return_value.append(existing_user)
            except ObjectDoesNotExist as ex:
                new_person = Person()
                new_person.sciper = base_data['sciper']
                new_person.username = base_data['username']
                if 'mail' in base_data:
                    new_person.email = base_data['mail']
                new_person.first_name = base_data['first_name']
                new_person.last_name = base_data['last_name']
                new_person.save()

                # Add the teacher to the teachers group for later use
                teachers_group.user_set.add(new_person)

                return_value.append(new_person)
    return return_value


def load_course(year='', term='', code='', subject='', types=list(), teachers=list(), students=int(), languages=list()):
    try:
        course = Course.objects.get(year=year, term=term, code=code)
    except ObjectDoesNotExist:
        course = Course()
        course.year = year
        course.term = term
        course.code = code
        course.subject = subject
        course.numberOfStudents = students
        if 'C' in types:
            course.has_course = True
        if 'Ex' in types:
            course.has_exercises = True
        if 'Proj' in types:
            course.has_project = True
        if 'TP' in types:
            course.has_practical_work = True

        if 'allemand' in languages:
            course.taughtInGerman = True
        if 'anglais' in languages:
            course.taughtInEnglish = True
        if 'français' in languages:
            course.taughtInFrench = True
        course.save()

    # time to deal with the teachings
    for teacher in teachers:
        try:
            teaching = Teaching.objects.get(person=teacher, course=course)
        except ObjectDoesNotExist:
            teaching = Teaching()
            teaching.person = teacher
            teaching.course = course
            teaching.save()


def load_mappings():
    filename = settings.FIRST_NAME_LAST_NAME_MAPPING
    names = list()
    import io
    with io.open(filename, 'r') as file:
        names = file.readlines()
    return_value = dict()
    for name in names:
        name = name.rstrip('\n')
        if not "*" in name and "Vacat ." not in name:
            last = name.split('/')[0].strip()
            first = name.split('/')[1].strip()
            entry_to_dump = epfl_ldap.get_user_by_partial_first_name_and_partial_last_name(
                settings, first, last)
            return_value[name.replace('/', '')] = entry_to_dump

    import pickle
    pickle_out = open(
        settings.PICKLED_DATA_FROM_LDAP, "wb")
    pickle.dump(return_value, pickle_out)
    pickle_out.close()


def check_groups_are_present():
    try:
        teachers = Group.objects.get(name="teachers")
    except ObjectDoesNotExist:
        teachers = Group()
        teachers.name = "teachers"
        teachers.save()

    try:
        phds = Group.objects.get(name="phds")
    except ObjectDoesNotExist:
        phds = Group()
        phds.name = "phds"
        phds.save()
