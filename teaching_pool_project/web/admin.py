# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Applications, Config, Topic, Person

admin.site.register(Topic)
admin.site.register(Config)
admin.site.register(Person)


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper


class ApplicationsInLine(admin.TabularInline):
    model = Applications
    verbose_name = 'Application'
    verbose_name_plural = 'Applications'


class ApplicationsAdmin(admin.ModelAdmin):
    list_display = ('custom_openedAt', 'custom_applicant',
                    'custom_course', 'status', 'custom_closedAt')
    list_filter = ['status',
                   ('openedAt', custom_titled_filter("opening date")),
                   ('closedAt', custom_titled_filter("closing date"))
                   ]
    search_fields = ['applicant', 'course', 'status']
    inline = [ApplicationsInLine]

    def custom_applicant(self, obj):
        return "{} {}.".format(obj.applicant.last_name, obj.applicant.first_name[:1])
    custom_applicant.short_description = "Applicant"

    def custom_course(self, obj):
        return "{} ({})".format(obj.course.subject, obj.course.code)
    custom_course.short_description = "Course"

    def custom_openedAt(self, obj):
        if obj.openedAt:
            return obj.openedAt.strftime('%d.%m.%Y')
    custom_openedAt.short_description = "Opened"

    def custom_closedAt(self, obj):
        if obj.closedAt:
            return obj.closedAt.strftime('%d.%m.%Y')
    custom_closedAt.short_description = "Closed"


admin.site.register(Applications, ApplicationsAdmin)
