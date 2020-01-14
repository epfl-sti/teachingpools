# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now

from epfl.sti.helpers import mail

from .validators import validate_year_config

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
    topics = models.ManyToManyField(
        "web.Topic", through="Interests", blank=True)
    section = models.ForeignKey(
        'Section', default=None, blank=True, null=True, on_delete=models.CASCADE)

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
    applications_withdrawn = models.IntegerField(default=0)

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


class Section(models.Model):
    name = models.CharField(max_length=255)

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
    TERM_CHOICES = [
        ('winter', 'winter'),
        ('summer', 'summer')
    ]
    term = models.CharField(max_length=255, choices=TERM_CHOICES)
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
        unique_together = [['year', 'term', 'person']]
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
        ('Declined', 'Declined'),
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

    def get_save_type(self):
        if not self.pk:
            return "created"
        elif self.status.lower() == "pending":
            return "updated"
        elif self.status.lower() == "approved":
            return "approved"
        elif self.status.lower() == "declined":
            return "declined"
        else:
            return None

    def save_and_notify(self, *args, **kwargs):
        action = self.get_save_type()

        # First actually save the instance
        super(NumberOfTAUpdateRequest, self).save(*args, **kwargs)

        # Update the related course object
        self.update_related_course(action=action)

        # Notify people if need be
        self.send_mail_on_TAs_requested(action=action)

    def update_related_course(self, action=None):
        if action:
            if action == "created":
                self.course.requestedNumberOfTAs = self.requestedNumberOfTAs
            elif action == "updated":
                self.course.requestedNumberOfTAs = self.requestedNumberOfTAs
            elif action == "approved":
                self.course.approvedNumberOfTAs = self.requestedNumberOfTAs
                self.course.requestedNumberOfTAs = None
            elif action == "declined":
                # we need to find the latest approved number of TAs
                latest_approved_number_of_TAs = NumberOfTAUpdateRequest.objects.filter(
                    course=self.course, status="Approved").order_by('-closedAt').first()
                if latest_approved_number_of_TAs:
                    self.course.approvedNumberOfTAs = latest_approved_number_of_TAs.requestedNumberOfTAs
                else:
                    self.course.approvedNumberOfTAs = None

                # Then we need to set the request nmber of TAs to the correct value
                self.course.requestedNumberOfTAs = None
            self.course.save()

    def send_mail_on_TAs_requested(self, *args, **kwargs):
        action = kwargs.get('action', None)
        if action == "created":
            # Generate the email notification
            data = {
                'request': self,
                'base_url': settings.APP_BASE_URL,
            }
            requesters = [teaching.person.email for teaching in Teaching.objects.filter(
                course=self.course)]
            admins_mails = settings.EMAIL_ADMINS_EMAIL

            if Config.objects.first().send_notification_to_admins_upon_ta_request:
                mail.notify_admins_and_requester(
                    data=data,
                    template_base='new_ta_request',
                    admins_subject='A new TA request has been recorded',
                    requesters_subject='Your request for TA has been recorded',
                    admins=admins_mails,
                    requesters=requesters)
            else:
                mail.notify_people(
                    data=data,
                    template="new_ta_request_requester",
                    subject='Your request for TA has been recorded',
                    sender=settings.EMAIL_FROM,
                    recipients=requesters
                )
        elif action == "updated":
            recipients = [teaching.person.email for teaching in Teaching.objects.filter(
                course=self.course)]
            mail.notify_people(
                data={'request': self},
                template='ta_request_approval',
                subject="Your request for TA has been {}".format(action),
                sender=settings.EMAIL_FROM,
                recipients=recipients)

        elif action == "approved" or action == "declined":
            recipients = [teaching.person.email for teaching in Teaching.objects.filter(
                course=self.course)]
            mail.notify_people(
                data={'request': self},
                template='ta_request_approval',
                subject="Your request for TA has been {}".format(action),
                sender=settings.EMAIL_FROM,
                recipients=recipients)
        else:
            pass


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
    SOURCE_CHOICES = [
        ('web', 'web'),
        ('system', 'system')
    ]
    source = models.CharField(max_length=255, default='web')
    ROLE_CHOICES = [
        ('TA', 'Teaching assistant'),
        ('AE', 'Assistant étudiant'),
    ]
    role = models.CharField(max_length=255, default='TA')

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

            # From there, there are several use cases
            # The use cases are based on 3 parameters:
            #   * the origin of the operation ['web', 'system'] TODO: it should be a good idea to revisit this to something like ['system', 'web - normal workflow', 'web - teacher request', 'web - section request']
            #   * the original state of the application [None, 'Pending', 'Hired', 'Rejected', 'Withdrawn']
            #   * the new state of the application [None, 'Pending', 'Hired', 'Rejected', 'Withdrawn']
            # This leads to 32 combinations that should be dealt with
            # The good news is that the origin of the operation is here to prevent sending emails when we are using a backoffice method to update the application.
            # Therefore all calls having a 'system' origin should not trigger a mail (which turns the number of combinations down to 16...).
            # We will only consider changes having an origin set as 'web'
            # The list of use cases are the following:
            # None -> None:           Use case 01: the application is not actually changing therefore, there's no reason to act upon it
            # None -> Pending:        Use case 02: 'regular workflow': the applicant should be notified his application is received and the teachers should be notified that they received a new application
            # None -> Hired:          Use case 03: Typically what happens when the teacher or the section hires the student directly. This should trigger a notification that the student has been enrolled to both the student and the teachers
            # None -> Rejected:       Use case 04: It should not happen. No need to act.
            # None -> Withdrawn:      Use case 04: It should not happen. No need to act.

            # Pending -> None:        Use case 04: It should not happen. No need to act.
            # Pending -> Pending:     Use case 01: the application is not actually changing therefore, there's no reason to act upon it
            # Pending -> Hired:       Use case 05: 'regular workflow'. This should trigger a notification to the student and the teachers
            # Pending -> Rejected:    Use case 05: 'regular workflow'. This should trigger a notification to the student and the teachers
            # Pending -> Withdrawn:   Use case 05: 'regular workflow'. This should trigger a notification to the student and the teachers

            # Hired -> None:          Use case 04: It should not happen. No need to act.
            # Hired -> Pending:       Use case 06: 'regular workflow'. This should trigger a notification to the student and the teachers
            # Hired -> Hired:         Use case 01: the application is not actually changing therefore, there's no reason to act upon it
            # Hired -> Rejected:      Use case 06: 'regular workflow'. This should trigger a notification to the student and the teachers
            # Hired -> Withdrawn:     Use case 06: 'regular workflow'. This should trigger a notification to the student and the teachers

            # Rejected -> None:       Use case 04: It should not happen. No need to act.
            # Rejected -> Pending:    Use case 06: 'regular workflow'. This should trigger a notification to the student and the teachers
            # Rejected -> Hired:      Use case 06: 'regular workflow'. This should trigger a notification to the student and the teachers
            # Rejected -> Rejected:   Use case 01: the application is not actually changing therefore, there's no reason to act upon it
            # Rejected -> Withdrawn:  Use case 04: It should not happen. No need to act.

            # Withdrawn -> None:      Use case 04: It should not happen. No need to act.
            # Withdrawn -> Pending:   Use case 04: It should not happen. No need to act.
            # Withdrawn -> Hired:     Use case 04: It should not happen. No need to act.
            # Withdrawn -> Rejected:  Use case 04: It should not happen. No need to act.
            # Withdrawn -> Withdrawn: Use case 01: the application is not actually changing therefore, there's no reason to act upon it

            # This leaves us with 6 possible use cases:
            # Use case 01: the application is not actually changing therefore, there's no reason to act upon it
            # Use case 02: 'regular workflow': the applicant should be notified his application is received and the teachers should be notified that they received a new application
            # Use case 03: Typically what happens when the teacher or the section hires the student directly. This should trigger a notification that the student has been enrolled to both the student and the teachers
            # Use case 04: It should not happen. No need to act.
            # Use case 05: 'regular workflow'. This should trigger a notification to the student and the teachers
            # Use case 06: 'regular workflow'. This should trigger a notification to the student and the teachers. However, this use case is different from Use case 05 because it is transition from a state that should be final (hired, rejected)


            use_case = None
            use_case = 1 if original_status == None and self.status == None else use_case
            use_case = 2 if original_status == None and self.status == "Pending" else use_case
            use_case = 3 if original_status == None and self.status == "Hired" else use_case
            use_case = 4 if original_status == None and self.status == "Rejected" else use_case
            use_case = 4 if original_status == None and self.status == "Withdrawn" else use_case

            use_case = 4 if original_status == "Pending" and self.status == None else use_case
            use_case = 1 if original_status == "Pending" and self.status == "Pending" else use_case
            use_case = 5 if original_status == "Pending" and self.status == "Hired" else use_case
            use_case = 5 if original_status == "Pending" and self.status == "Rejected" else use_case
            use_case = 5 if original_status == "Pending" and self.status == "Withdrawn" else use_case

            use_case = 4 if original_status == "Hired" and self.status == None else use_case
            use_case = 6 if original_status == "Hired" and self.status == "Pending" else use_case
            use_case = 1 if original_status == "Hired" and self.status == "Hired" else use_case
            use_case = 6 if original_status == "Hired" and self.status == "Rejected" else use_case
            use_case = 6 if original_status == "Hired" and self.status == "Withdrawn" else use_case

            use_case = 4 if original_status == "Rejected" and self.status == None else use_case
            use_case = 6 if original_status == "Rejected" and self.status == "Pending" else use_case
            use_case = 6 if original_status == "Rejected" and self.status == "Hired" else use_case
            use_case = 1 if original_status == "Rejected" and self.status == "Rejected" else use_case
            use_case = 4 if original_status == "Rejected" and self.status == "Withdrawn" else use_case

            use_case = 4 if original_status == "withdrawn" and self.status == None else use_case
            use_case = 4 if original_status == "withdrawn" and self.status == "Pending" else use_case
            use_case = 4 if original_status == "withdrawn" and self.status == "Hired" else use_case
            use_case = 4 if original_status == "withdrawn" and self.status == "Rejected" else use_case
            use_case = 1 if original_status == "withdrawn" and self.status == "Withdrawn" else use_case

            if use_case == 1:
                # the application is not actually changing therefore, there's no reason to act upon it
                pass
            elif use_case == 2:
                # 'regular workflow': the applicant should be notified his application is received and the teachers should be notified that they received a new application
                # None -> Pending

                    # we only want to notify people when the application has been recorded through the web interface
                    if self.source == 'web':
                        # Notify people of this change
                        data = {
                            'course': self.course,
                            'application': self,
                            'base_url': settings.APP_BASE_URL,
                        }
                        requesters = list()
                        requesters.append(self.applicant.email)
                        admins = [item.email for item in self.course.teachers.all()]

                        mail.notify_admins_and_requester(
                            data=data,
                            template_base='new_application',
                            admins_subject='A new application as TA or AE has been recorded for your course',
                            requesters_subject='Your application has been recorded',
                            admins=admins,
                            requesters=requesters)

            elif use_case == 3:
                # Typically what happens when the teacher or the section hires the student directly. This should trigger a notification that the student has been enrolled to both the student and the teachers
                # None -> Hired

                # we only want to notify people when the application has been recorded through the web interface
                if self.source == 'web':
                    # Notify people of this change
                    data = {
                        'course': self.course,
                        'application': self,
                    }
                    requesters = list()
                    requesters.append(self.applicant.email)
                    admins = [item.email for item in self.course.teachers.all()]

                    mail.notify_admins_and_requester(
                        data=data,
                        template_base='student_enrolled',
                        admins_subject='A student has been enrolled as {} for your course'.format(self.role),
                        requesters_subject='You have been enrolled for a teaching duty',
                        admins=admins,
                        requesters=requesters)

            elif use_case == 4:
                # It should not happen. No need to act.
                # None -> Rejected
                # None -> Withdrawn
                # Pending -> None
                # Hired -> None
                # Rejected -> None
                # Rejected -> Withdrawn
                # Withdrawn -> None
                # Withdrawn -> Pending
                # Withdrawn -> Hired
                # Withdrawn -> Rejected
                pass
            elif use_case == 5:
                # 'regular workflow'. This should trigger a notification to the student and the teachers
                # Pending -> Hired
                # Pending -> Rejected
                # Pending -> Withdrawn

                # we only want to notify people when the application has been recorded through the web interface
                if self.source == 'web':
                    # Notify people
                    data = {
                        'application': self,
                    }
                    requesters = list()
                    requesters.append(self.applicant.email)
                    admins = [item.email for item in self.course.teachers.all()]

                    mail.notify_admins_and_requester(
                        data=data,
                        template_base='processed_application',
                        admins_subject = 'An application as {} for your course has been updated'.format(self.role),
                        requesters_subject='Your application has been processed',
                        admins=admins,
                        requesters=requesters)

            elif use_case == 6:
                # 'regular workflow': the applicant should be notified his application is received and the teachers should be notified that they received a new application
                # Hired -> Pending
                # Hired -> Rejected
                # Hired -> Withdrawn
                # Rejected -> Pending
                # Rejected -> Hired

                if self.source == 'web':
                    # Notify people
                    data = {
                        'application': self,
                    }
                    requesters = list()
                    requesters.append(self.applicant.email)
                    admins = [item.email for item in self.course.teachers.all()]

                    mail.notify_admins_and_requester(
                        data=data,
                        template_base='processed_application',
                        admins_subject = 'An application as {} for your course has been updated'.format(self.role),
                        requesters_subject='Your application has been processed',
                        admins=admins,
                        requesters=requesters)


            # if original_status == None:
            #     if self.status == "Pending":
            #         # Update the counters of the course
            #         self.course.applications_received = self.course.applications_received + 1
            #         self.course.save()

            # if original_status == "Pending":
            #     if self.status == "Rejected":

            #         # Update the course counters
            #         self.course.applications_rejected = self.course.applications_rejected + 1
            #         self.course.save()

            #     # Pending -> Hired
            #     elif self.status == "Hired":

            #         # Update the course counters
            #         self.course.applications_accepted = self.course.applications_accepted + 1
            #         self.course.save()

            # if self.status == "Withdrawn":
            #     # Update the course counters
            #     if original_status == "Pending":
            #         self.course.applications_received -= 1
            #         self.course.applications_withdrawn += 1
            #         self.course.save()
            #     elif original_status == "Hired":
            #         self.course.applications_accepted -= 1
            #         self.course.applications_withdrawn += 1
            #         self.course.save()
            #     elif original_status == "Rejected":
            #         self.course.applications_rejected -= 1
            #         self.course.applications_withdrawn += 1
            #         self.course.save()
            #     elif original_status == "Withdrawn":
            #         # There is actually nothing to do and this case should not happen.
            #         # This code is here for the sole purpose of covering all cases.
            #         pass

    class Meta:
        indexes = [
            models.Index(fields=['applicant']),
            models.Index(fields=['course']),
            models.Index(fields=['status']),
        ]


class Config(models.Model):
    current_year = models.CharField(
        max_length=9, validators=[validate_year_config])
    TERM_CHOICES = [
        ('HIVER', 'HIVER'),
        ('ETE', 'ETE')
    ]
    current_term = models.CharField(max_length=6, choices=TERM_CHOICES)
    requests_for_TAs_are_open = models.BooleanField(default=True)
    applications_are_open = models.BooleanField(default=True)
    send_notification_to_admins_upon_ta_request = models.BooleanField(default=True)
    phds_can_withdraw_applications = models.BooleanField(default=True)

    def __str__(self):
        return '{} - {}'.format(self.current_year, self.current_term)

    def save(self, *args, **kwargs):
        if Config.objects.exists() and not self.pk:
            raise ValidationError(
                "There can only be one instance of the configuration")
        return super(Config, self).save(*args, **kwargs)
