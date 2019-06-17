# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Person(models.Model):
    ROLE_CHOICES = [
        ('teacher', 'teacher'),
        ('teaching assistant', 'teaching assistant')
    ]

    sciper = models.IntegerField(
        verbose_name="EPFL sciper", name="sciper", primary_key=True)
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    email = models.EmailField(default=None, blank=True, null=True)
    role = models.CharField(
        max_length=255, choices=ROLE_CHOICES, default="teacher")
    courses = models.ManyToManyField("web.Course", through='Teaching')

    def __str__(self):
        return "{last}, {first} ({sciper})".format(last=self.lastName, first=self.firstName, sciper=self.sciper)

    class Meta:
        ordering = ('lastName', 'firstName')


class Course(models.Model):
    academicYear = models.CharField(max_length=9, name="year")
    academicTerm = models.CharField(max_length=255, name="term")
    code = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    section = models.CharField(max_length=255)
    numberOfStudents = models.IntegerField()
    teachers = models.ManyToManyField("web.Person", through="Teaching")

    def __str__(self):
        return "{year} - {term} - {code}".format(year=self.academicYear, term=self.academicTerm, code=self.code)

    class Meta:
        ordering = ('year', 'term', 'code')
        unique_together = [['year', 'term', 'code']]
        index_together = [
            ['year', 'term', 'code'],
        ]


class Teaching(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
