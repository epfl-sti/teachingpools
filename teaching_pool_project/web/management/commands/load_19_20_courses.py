import io
import logging
import os.path
import pickle
from math import ceil

import numpy as np
import pandas as pd
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from web.models import Course, Person, Teaching

logger = logging.getLogger(__name__)


def load_course(row):
    year = row['year']
    term = row['term']
    code = row['code']
    subject = row['topic']
    raw_teachers = row['teachers']
    students = int(np.nan_to_num(row['numberOfStudents']))
    has_course = row['has_course']
    has_exercises = row['has_exercises']
    has_project = row['has_project']
    has_practical_work = row['has_practical_work']
    taughtInFrench = row['taughtInFrench']
    taughtInEnglish = row['taughtInEnglish']
    taughtInGerman = row['taughtInGerman']

    try:
        course = Course.objects.get(year=year, term=term, code=code)
    except ObjectDoesNotExist:
        course = Course()
        course.year = year
        course.term = term
        course.code = code

    course.subject = subject
    course.numberOfStudents = students
    course.taughtInFrench = taughtInFrench
    course.taughtInEnglish = taughtInEnglish
    course.taughtInGerman = taughtInGerman
    course.has_course = has_course
    course.has_exercises = has_exercises
    course.has_project = has_project
    course.has_practical_work = has_practical_work

    if course.has_exercises or course.has_practical_work:
        course.calculatedNumberOfTAs = int(ceil((course.numberOfStudents/25)))
    else:
        course.calculatedNumberOfTAs = 0

    course.save()


def load_teacher(row):
    sciper = row['sciper']

    try:
        teacher = Person.objects.get(sciper=sciper)
    except ObjectDoesNotExist:
        teacher = Person()
        teacher.sciper = row['sciper']
        teacher.username = row['username']
        teacher.first_name = row['first_name']
        teacher.last_name = row['last_name']
        teacher.email = row['mail']
        teacher.save()

    teachers_group = Group.objects.get(name="teachers")
    if not teacher.groups.filter(name="teachers").exists():
        teachers_group.user_set.add(teacher)
        teachers_group.save()
        teacher.save()


def load_course_teachings(course, teachers):
    # get the course in database
    year = course['year']
    term = course['term']
    code = course['code']

    # load the course saved in the database
    db_course = Course.objects.get(year=year, term=term, code=code)

    # Loop over the teachers to load the teachings
    for teacher in course['teachers']:

        # find the sciper of the current teacher
        mask = teachers['ISA'] == teacher
        sciper = teachers[mask].iloc[0]['sciper']

        db_user = Person.objects.get(sciper=sciper)

        # Check if the teacher is already registered as a teacher for this course
        try:
            teaching = Teaching.objects.get(course=db_course, person=db_user)
        except ObjectDoesNotExist:
            # Create the teaching activity
            teaching = Teaching()
            teaching.course = db_course
            teaching.person = db_user
            teaching.save()


class Command(BaseCommand):
    def handle(self, **options):
        # Load the courses into the database
        courses = pd.read_pickle(settings.COURSE_LOADER_COURSE_PICKLE_PATH)
        courses.apply(lambda row: load_course(row), axis=1)

        # Load the teachers into the database
        teachers = pd.read_pickle(settings.COURSE_LOADER_TEACHERS_PICKLE_PATH)
        teachers.apply(lambda row: load_teacher(row), axis=1)

        # Load the teachings into the database
        courses.apply(lambda course: load_course_teachings(course, teachers), axis=1)
