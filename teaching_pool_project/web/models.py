# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now

from epfl.sti.helpers import mail

logger = logging.getLogger(__name__)


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
    canTeachInGerman = models.BooleanField(
        null=True, blank=True, default=None)
    topics = models.ManyToManyField("web.Topic", through="Interests", blank=True)

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
    taughtInFrench = models.BooleanField(default=False)
    taughtInEnglish = models.BooleanField(default=False)
    taughtInGerman = models.BooleanField(default=False)
    has_course = models.BooleanField(default=False)
    has_exercises = models.BooleanField(default=False)
    has_project = models.BooleanField(default=False)
    has_practical_work = models.BooleanField(default=False)
    applications_received = models.IntegerField(default=0)
    applications_accepted = models.IntegerField(default=0)
    applications_rejected = models.IntegerField(default=0)

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

    def __str__(self):
        return self.name


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

    def save(self, *args, **kwargs):
        if not self.pk:
            logger.info("Saving a new request for TAs")

            # First, actually save the model since we need the primary key to generate the email template
            super(NumberOfTAUpdateRequest, self).save(*args, **kwargs)

            # Update the number of requested TAs on the course object
            self.course.requestedNumberOfTAs = self.requestedNumberOfTAs
            self.course.save()

            # Generate the email notification
            data = {
                'request': self,
                'base_url': settings.APP_BASE_URL,
            }
            requesters = list()
            requesters.append(self.requester.email)
            admins_mails = settings.EMAIL_ADMINS_EMAIL

            mail.notify_admins_and_requester(
                data=data,
                template_base='new_ta_request',
                admins_subject='A new TA request has been recorded',
                requesters_subject='Your request for TA has been recorded',
                admins=admins_mails,
                requesters=requesters)

        else:
            logger.info("Updating request for TA")

            # First, actually save the model since we need the status to be correct to update the course object
            super(NumberOfTAUpdateRequest, self).save(*args, **kwargs)

            # Update the course object in order to reflect the decision made
            latest_approved_request = NumberOfTAUpdateRequest.objects \
                .filter(course=self.course, status="Approved") \
                .order_by('-closedAt') \
                .first()
            if latest_approved_request:
                self.course.approvedNumberOfTAs = latest_approved_request.requestedNumberOfTAs
            else:
                self.course.approvedNumberOfTAs = None
            self.course.save()

            latest_requested_request = NumberOfTAUpdateRequest.objects \
                .filter(course=self.course, status="Pending") \
                .order_by('-openedAt') \
                .first()
            if latest_requested_request:
                self.course.requestedNumberOfTAs = latest_requested_request.requestedNumberOfTAs
            else:
                self.course.requestedNumberOfTAs = None

            self.course.save()

            # Generate the email notification
            notification_recipients = list()
            notification_recipients.append(self.requester.email)
            if self.status.lower() == "pending":
                subject_status = "updated"
            else:
                subject_status = self.status.lower()

            mail.notify_people(
                data={'request': self},
                template="ta_request_approval",
                subject="Your request for TA has been {}".format(subject_status),
                sender=settings.EMAIL_FROM,
                recipients=notification_recipients)

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

    def save(self, *args, **kwargs):
        # Detect if it is a brand new application
        if not self.pk:
            created = True
        else:
            created = False

        # Get the original status if we can get one
        if not created:
            original_status = Applications.objects.get(pk=self.pk).status
        else:
            original_status = None

        # Call the super save in order to get a primary key
        super(Applications, self).save(*args, **kwargs)

        # We only want to act on applications changing status
        if self.status != original_status:
            if original_status == None:
                if self.status == "Pending":
                    # Notify people of this change
                    data = {
                        'course': self.course,
                        'application': self,
                        'base_url': settings.APP_BASE_URL,
                    }
                    requesters = list()
                    requesters.append(self.applicant.email)
                    destinations = [
                        item.email for item in self.course.teachers.all()]

                    mail.notify_admins_and_requester(
                        data=data,
                        template_base='new_application',
                        admins_subject='A new teaching assistant application has been recorded for your course',
                        requesters_subject='Your application has been recorded',
                        admins=destinations,
                        requesters=requesters)

                    # Update the counters of the course
                    self.course.applications_received = self.course.applications_received + 1
                    self.course.save()

            if original_status == "Pending":
                if self.status == "Rejected":
                    data = {
                        'application': self,
                    }
                    requesters = list()
                    requesters.append(self.applicant.email)

                    mail.notify_people(
                        data=data,
                        template='processed_application',
                        subject='Your application has been {}'.format(
                            self.status.lower()),
                        sender=settings.EMAIL_FROM,
                        recipients=requesters)

                    # Update the course counters
                    self.course.applications_rejected = self.course.applications + 1
                    self.course.save()

                # Pending -> Hired
                elif self.status == "Hired":

                    # Notify people
                    data = {
                        'application': self,
                    }
                    requesters = list()
                    requesters.append(self.applicant.email)

                    mail.notify_people(
                        data=data,
                        template='processed_application',
                        subject='Your application has been processed',
                        sender=settings.EMAIL_FROM,
                        recipients=requesters)

                    # Update the course counters
                    self.course.applications_accepted = self.course.applications_accepted + 1
                    self.course.save()

    class Meta:
        indexes = [
            models.Index(fields=['applicant']),
            models.Index(fields=['course']),
            models.Index(fields=['status']),
        ]
