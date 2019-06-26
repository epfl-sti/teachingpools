# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


class Person(AbstractUser):
    ROLE_CHOICES = [
        ('teacher', 'teacher'),
        ('teaching assistant', 'teaching assistant')
    ]

    sciper = models.IntegerField(null=True, blank=True, default=None)
    role = models.CharField(
        max_length=255, choices=ROLE_CHOICES, default="teacher")
    courses = models.ManyToManyField("web.Course", through='Teaching')
    canTeachInFrench = models.BooleanField(null=True, blank=True, default=None)
    canTeachInEnglish = models.BooleanField(
        null=True, blank=True, default=None)
    topics = models.ManyToManyField("web.Topic", through="Interests")

    def __str__(self):
        return "{last}, {first} ({id})".format(last=self.last_name, first=self.first_name, id=self.id)

    class Meta:
        ordering = ('last_name', 'first_name')


class Course(models.Model):
    year = models.CharField(max_length=9)
    term = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    section = models.CharField(max_length=255)
    numberOfStudents = models.IntegerField()
    calculatedNumberOfTAs = models.IntegerField(
        null=True, blank=True, default=None)
    requestedNumberOfTAs = models.IntegerField(
        null=True, blank=True, default=None)
    approvedNumberOfTAs = models.IntegerField(
        null=True, blank=True, default=None)
    teachers = models.ManyToManyField("web.Person", through="Teaching")
    taughtInFrench = models.BooleanField(default=True)
    taughtInEnglish = models.BooleanField(default=False)
    taughtInGerman = models.BooleanField(default=False)
    has_course = models.BooleanField(default=False)
    has_exercises = models.BooleanField(default=False)
    has_project = models.BooleanField(default=False)
    has_practical_work = models.BooleanField(default=False)

    def __str__(self):
        return "{year} - {term} - {code}".format(year=self.year, term=self.term, code=self.code)

    class Meta:
        ordering = ('year', 'term', 'code')
        unique_together = [['year', 'term', 'code']]
        index_together = [
            ['year', 'term', 'code'],
            ['year', 'term'],
        ]
        indexes = [
            models.Index(fields=['year'], name='year_idx'),
            models.Index(fields=['code'], name='code_idx'),
            models.Index(fields=['section'], name='section_idx'),
            models.Index(fields=['taughtInFrench'], name='french_idx'),
            models.Index(fields=['taughtInFrench'], name='english_idx'),
        ]


class Teaching(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=255, default=None, blank=True, null=True)
    isLeadTeacher = models.BooleanField(default=None, blank=True, null=True)

    def __str__(self):
        return "{} -> {}".format(self.person, self.course)

    class Meta:
        unique_together = [['person', 'course']]
        indexes = [
            models.Index(fields=['person']),
            models.Index(fields=['course'])
        ]


class Topic(models.Model):
    name = models.CharField(max_length=255)
    interestedPersons = models.ManyToManyField(
        "web.Person", through="Interests")


class Interests(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    def __str__(self):
        return "{} -> {}".format(self.person, self.topic)

    class Meta:
        unique_together = [['person', 'topic']]
        indexes = [
            models.Index(fields=['person']),
            models.Index(fields=['topic'])
        ]


class Availability(models.Model):
    year = models.CharField(max_length=9)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    AVAILABILITIES_CHOICES = [
        ('Available', 'Available'),
        ('Unavailable', 'Unavailable')
    ]
    availability = models.CharField(
        max_length=255, choices=AVAILABILITIES_CHOICES, default="Available")
    reason = models.TextField(null=True, blank=True, default=None)

    def __str__(self):
        return "{} -> {} -> {}".format(self.year, self.person, self.availability)

    class Meta:
        unique_together = [['year', 'person']]
        index_together = [
            ['year', 'person']
        ]
        indexes = [
            models.Index(fields=['year']),
            models.Index(fields=['person'])
        ]


class NumberOfTAUpdateRequest(models.Model):
    openedAt = models.DateTimeField(default=now)
    requester = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="requester")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    requestedNumberOfTAs = models.IntegerField()
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Withdrawn', 'Withdrawn')
    ]
    status = models.CharField(max_length=255, default='Pending')
    requestReason = models.TextField(null=True, blank=True, default=None)
    closedAt = models.DateTimeField(default=None, null=True, blank=True)
    decidedBy = models.ForeignKey(
        Person, on_delete=models.CASCADE, default=None, null=True, blank=True, related_name="decidedBy")
    decisionReason = models.TextField(null=True, blank=True, default=None)

    class Meta:
        indexes = [
            models.Index(fields=['requester']),
            models.Index(fields=['course']),
            models.Index(fields=['status']),
        ]


class Applications(models.Model):
    openedAt = models.DateTimeField(default=now)
    applicant = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="applicant")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Hired', 'Hired'),
        ('Rejected', 'Rejected'),
        ('Withdrawn', 'Withdrawn')
    ]
    status = models.CharField(max_length=255, default='Pending')
    closedAt = models.DateTimeField(default=None, blank=True, null=True)
    closedBy = models.ForeignKey(
        Person, on_delete=models.CASCADE, default=None, null=True, blank=True)
    decisionReason = models.TextField(null=True, blank=True, default=None)

    def __str__(self):
        return "{} -> {} -> {}".format(self.applicant, self.course, self.status)

    class Meta:
        indexes = [
            models.Index(fields=['applicant']),
            models.Index(fields=['course']),
            models.Index(fields=['status']),
        ]
