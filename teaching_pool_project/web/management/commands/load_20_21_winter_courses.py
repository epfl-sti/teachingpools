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
from ldap3 import ALL, Connection, Server
from ldap3.core.exceptions import LDAPInvalidFilterError

from web.models import Course, Person, Teaching

logger = logging.getLogger(__name__)


def load_course(row):
    year = row["year"]
    term = row["term"]
    code = row["code"]
    subject = row["topic"]
    raw_teachers = row["teachers"]
    prev_year_students = int(np.nan_to_num(row["prev_year_registered_students"]))

    if not pd.isnull(row["course_forms"]):
        has_course = "c" in row["course_forms"].lower()
        has_exercises = "ex" in row["course_forms"].lower()
        has_project = "proj" in row["course_forms"].lower()
        has_practical_work = "tp" in row["course_forms"].lower()
    else:
        has_course = False
        has_exercises = False
        has_project = False
        has_practical_work = False

    if not pd.isnull(row["course_languages"]):
        taughtInFrench = "français" in row["course_languages"].lower()
        taughtInEnglish = "anglais" in row["course_languages"].lower()
        taughtInGerman = "allemand" in row["course_languages"].lower()
    else:
        taughtInFrench = False
        taughtInEnglish = False
        taughtInGerman = False

    try:
        course = Course.objects.get(year=year, term=term, code=code)
    except ObjectDoesNotExist:
        course = Course()
        course.year = year
        course.term = term
        course.code = code

    course.subject = subject
    course.numberOfStudents = prev_year_students
    course.taughtInFrench = taughtInFrench
    course.taughtInEnglish = taughtInEnglish
    course.taughtInGerman = taughtInGerman
    course.has_course = has_course
    course.has_exercises = has_exercises
    course.has_project = has_project
    course.has_practical_work = has_practical_work

    if course.has_exercises or course.has_practical_work:
        course.calculatedNumberOfTAs = int(ceil((course.numberOfStudents / 25)))
    else:
        course.calculatedNumberOfTAs = 0

    course.save()


def load_teacher(row):
    logger.info("loading teacher")
    logger.debug(row["sciper"])
    sciper = row["sciper"]
    if pd.isnull(sciper):
        logger.warning("Teacher not added because the sciper is null")
        return

    try:
        teacher = Person.objects.get(sciper=sciper)
    except ObjectDoesNotExist:
        teacher = Person()
        teacher.sciper = row["sciper"]
        teacher.username = row["teacher_username"]
        teacher.first_name = get_firstname(row["sciper"])
        teacher.last_name = get_lastname(row["sciper"])
        teacher.email = get_email(row["sciper"])
        if (
            pd.isnull(teacher.first_name)
            or pd.isnull(teacher.last_name)
            or pd.isnull(teacher.email)
        ):
            logger.warning(
                "teacher not saved because he does not have a first name or a last name or an email address"
            )
            return
        else:
            logger.debug("saving teacher")
            teacher.save()

    teachers_group = Group.objects.get(name="teachers")
    if teacher.groups.filter(name="teachers").exists() == False:
        logger.debug("adding teacher to group")
        teachers_group.user_set.add(teacher)
        teachers_group.save()
        teacher.save()
    else:
        logger.debug("teacher already part of the group")


def load_course_teachings(row):
    logger.info("loading teaching into DB")

    # get the course in database
    year = row["year"]
    term = row["term"]
    code = row["code"]

    # load the course saved in the database
    db_course = Course.objects.get(year=year, term=term, code=code)

    sciper = row["sciper"]
    if pd.isnull(sciper):
        logger.warning(
            "Unable to load teaching because the person cannot be found (sciper null)"
        )
        return
    try:
        db_user = Person.objects.get(sciper=sciper)
    except ObjectDoesNotExist:
        logger.warning("unable to find user in DB (sciper: {})".format(sciper))
        return

    try:
        teaching = Teaching.objects.get(course=db_course, person=db_user)
    except ObjectDoesNotExist:
        # Create the teaching activity
        teaching = Teaching()
        teaching.course = db_course
        teaching.person = db_user
        teaching.save()


def get_username(row):
    sciper = row["sciper enseignant"]

    filter = "(uniqueIdentifier={sciper})".format(sciper=sciper)
    ldap_server = Server(settings.LDAP_SERVER, use_ssl=True, get_info=ALL)
    conn = Connection(ldap_server, auto_bind=True)
    conn.search(settings.LDAP_BASEDN, filter, attributes=["uid"], size_limit=1)
    if len(conn.entries) == 1:
        entry = conn.entries[0]
        uid = entry["uid"].value
        if isinstance(uid, list):
            uid = uid[0]
        if "@" in uid:
            uid = uid.split("@")[0]
        return uid


def get_firstname(sciper):
    filter = "(uniqueIdentifier={sciper})".format(sciper=sciper)
    ldap_server = Server(settings.LDAP_SERVER, use_ssl=True, get_info=ALL)
    conn = Connection(ldap_server, auto_bind=True)
    conn.search(settings.LDAP_BASEDN, filter, attributes=["givenName"], size_limit=1)
    if len(conn.entries) == 1:
        entry = conn.entries[0]
        givenName = entry["givenName"].value
        if isinstance(givenName, list):
            givenName = givenName[0]
        return givenName


def get_lastname(sciper):
    filter = "(uniqueIdentifier={sciper})".format(sciper=sciper)
    ldap_server = Server(settings.LDAP_SERVER, use_ssl=True, get_info=ALL)
    conn = Connection(ldap_server, auto_bind=True)
    conn.search(settings.LDAP_BASEDN, filter, attributes=["sn"], size_limit=1)
    if len(conn.entries) == 1:
        entry = conn.entries[0]
        sn = entry["sn"].value
        if isinstance(sn, list):
            sn = sn[0]
        return sn


def get_email(sciper):
    filter = "(uniqueIdentifier={sciper})".format(sciper=sciper)
    ldap_server = Server(settings.LDAP_SERVER, use_ssl=True, get_info=ALL)
    conn = Connection(ldap_server, auto_bind=True)
    conn.search(settings.LDAP_BASEDN, filter, attributes=["mail"], size_limit=1)
    if len(conn.entries) == 1:
        entry = conn.entries[0]
        mail = entry["mail"].value
        if isinstance(mail, list):
            mail = mail[0]
        return mail


class Command(BaseCommand):
    def handle(self, **options):
        logger.info("starting to load courses")
        # Load the courses into the database
        # courses = pd.read_excel(settings.DJANGO_COURSE_LOADER_COURSES_EXCEL_FILE)
        # courses = pd.read_excel(
        #     "./teaching_pool_project/data/2020-2021_HIVER/liste_matières_STI.xlsx",
        #     sheet_name="Liste matières (1 ligne par ens",
        #     skiprows=2,
        #     dtype={"sciper enseignant": object},
        # )

        # # set the username of the teacher if it is not already provided
        # courses["teacher_username"] = courses.apply(
        #     lambda row: get_username(row), axis=1
        # )

        courses = pd.read_excel(
            "./teaching_pool_project/data/2020-2021_HIVER/liste_matières_STI.xlsx",
            sheet_name="stiteachingpools",
            dtype={"sciper enseignant": object},
        )

        courses.rename(
            columns={
                "codification cours": "code",
                "Matières": "topic",
                "enseignant (nom,prénom)": "teachers",
                "sciper enseignant": "sciper",
                "semestre plan": "term",
                "forme cours": "course_forms",
                "nombre d'inscriptions via les plans STI": "registered_students_through_plan",
                "nombre total d'inscription": "numberOfStudents",
                "langue d'enseignement": "course_languages",
            },
            inplace=True,
        )

        courses.drop(columns=["registered_students_through_plan"], inplace=True)

        courses["year"] = "2020-2021"

        # Load the courses into the database
        courses.apply(lambda row: load_course(row), axis=1)

        # Load the teachers into the database
        courses.apply(lambda row: load_teacher(row), axis=1)

        # Load the teachings into the database
        courses.apply(lambda row: load_course_teachings(row), axis=1)

        logger.info("done")
