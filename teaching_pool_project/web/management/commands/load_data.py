import io
import logging
import os.path
import pickle
from math import ceil

import numpy
import pandas as pd
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from epfl.sti.helpers import ldap as epfl_ldap
from web.models import Course, Person, Teaching

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, **options):
        logger.info("loading courses for the current year")

        # Sanity check to make sure that the required groups are present
        check_groups_are_present()

        # Load the courses for the current year
        df = pd.read_excel(settings.EXCEL_FILE_TO_LOAD)
        for index, row in df.iterrows():
            if type(row['code']) != type(str()):
                course_code = ''
            else:
                course_code = row['code']
            subject = row['subject']
            if type(row['teachers']) != type(float()):
                raw_teachers = [x.strip() for x in row['teachers'].split(';')]
            else:
                raw_teachers = list()
            term = row['term']
            if type(row['type']) != type(float()):
                raw_types = [x.lower().strip() for x in row['type'].split(',')]
            else:
                raw_types = list()

            if numpy.isnan(row['students']):
                row['students'] = numpy.nan_to_num(row['students'])
            students = int(row['students'])

            if type(row['languages']) != type(float()):
                raw_languages = [x.lower().strip()
                                 for x in row['languages'].split('/')]
            else:
                raw_languages = list()

            teachers = load_teachers(raw_teachers)

            if settings.EXCEL_LOADER_CURRENT_YEAR and term and course_code:
                load_course(settings.EXCEL_LOADER_CURRENT_YEAR, term, course_code,
                            subject, raw_types, teachers, students, raw_languages)

        # Now time to load the stats for the previous year
        logger.info("Loading statistics from the previous year")
        df = pd.read_excel(settings.EXCEL_FILE_TO_LOAD_FOR_PREVIOUS_YEAR)
        for index, row in df.iterrows():

            if type(row['code']) != type(str()):
                course_code = ''
            else:
                course_code = row['code']

            if type(row['term']) != type(str()):
                term = ''
            else:
                term = row['term']

            if numpy.isnan(row['students']):
                row['students'] = numpy.nan_to_num(row['students'])
            students = int(row['students'])

            if settings.EXCEL_LOADER_CURRENT_YEAR and term and course_code:
                update_course(settings.EXCEL_LOADER_CURRENT_YEAR,
                            term, course_code, students)
            else:
                logger.warning("Unable to update course because one of the mandatory field was not provided")
                logger.debug("year: %s", settings.EXCEL_LOADER_CURRENT_YEAR)
                logger.debug("term: %s", term)
                logger.debug("code: %s", course_code)
                logger.debug("students: %s", students)


def update_course(year, term, code, students):
    logger.info("Updating number of students")
    logger.debug("year: %s", year)
    logger.debug("term: %s", term)
    logger.debug("code: %s", code)
    logger.debug("students: %s", students)

    if not year or not term or not code or type(students)!=type(int()):
        error_message = "A least one of the fields did not have a correct value"
        logger.error(error_message)
        raise ValueError("A least one of the fields did not have a correct value")

    try:
        course = Course.objects.get(year__iexact=year, term__iexact=term, code__iexact=code)
        course.numberOfStudents = students
        if course.has_exercises or course.has_practical_work:
            course.calculatedNumberOfTAs = int(ceil((students/25)))
        else:
            course.calculatedNumberOfTAs = 0

        course.save()
    except ObjectDoesNotExist:
        logger.warning("Unable to find course")


def load_teachers(teachers=list()):
    logger.info("loading teachers")
    logger.debug("teachers: %s", teachers)

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
    logger.info("loading course")
    logger.debug("year: %s", year)
    logger.debug("term: %s", term)
    logger.debug("code: %s", code)
    logger.debug("subject: %s", subject)
    logger.debug("types: %s", types)
    logger.debug("teachers: %s", teachers)
    logger.debug("students: %s", students)
    logger.debug("languages: %s", languages)


    # We don't want to manage courses that fill the minimum requirements
    if year == '' or term == '' or code == '':
        error_message = "At least one mandatory field (year, term, code) was not passed."
        logger.error(error_message)
        raise ValueError(error_message)

    course, course_created = Course.objects.get_or_create(year__iexact=year, term__iexact=term, code__iexact=code)

    if course_created:
        logger.debug("new course")

    course.year = year
    course.term = term
    course.code = code
    course.subject = subject
    course.numberOfStudents = students
    course.has_course = 'c' in types
    course.has_exercises = 'ex' in types
    course.has_project = 'proj' in types
    course.has_practical_work = 'tp' in types
    course.taughtInGerman = 'allemand' in languages
    course.taughtInEnglish = 'anglais' in languages
    course.taughtInFrench = 'français' in languages

    course.save()

    # time to deal with the teachings
    for teacher in teachers:
        teaching, teaching_created = Teaching.objects.get_or_create(person=teacher, course=course)
        if teaching_created:
            teaching.person = teacher
            teaching.course = course
            teaching.save()


def load_mappings():
    logger.info("loading mappings file")

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
    logger.info("checking base groups (teachers, phds) ar existing")
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
