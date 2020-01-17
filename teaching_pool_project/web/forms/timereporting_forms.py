import re

from crispy_forms.bootstrap import (AppendedText, FormActions, InlineRadios,
                                    Tab, TabHolder)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (HTML, Button, Column, Div, Field, Layout,
                                 Reset, Row, Submit)
from django.contrib.auth.models import Group
from django.forms import ModelChoiceField, ModelForm, TextInput
from django.urls import reverse

from web.models import *


class CourseClassChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "{} - {} - {}".format(obj.year, obj.term, obj.subject)


class TeacherChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "{}, {}".format(obj.last_name, obj.first_name)


class TimeReportForm(ModelForm):
    class Meta:
        model = TimeReport
        fields = '__all__'
        initial_fields = ['created_by']
        field_classes = {
            'class_teaching_course': CourseClassChoiceField,
            'master_thesis_teacher_in_charge': TeacherChoiceField,
            'semester_project_teacher_in_charge': TeacherChoiceField,
            'other_job_teacher_in_charge': TeacherChoiceField,
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(TimeReportForm, self).__init__(*args, **kwargs)

        # restrict the dropdown lists to actual teachers
        teachers = Group.objects.get(name="teachers").user_set.all()
        self.fields['master_thesis_teacher_in_charge'].queryset = teachers
        self.fields['semester_project_teacher_in_charge'].queryset = teachers
        self.fields['other_job_teacher_in_charge'].queryset = teachers

        # Restrict the list of users to the currently logged in user to improve performances
        self.fields['created_by'].queryset = Person.objects.filter(id=user.id).all()

        # Restrict the list of courses to the Hired applications
        courses_keys = Applications.objects.filter(applicant=user, status="Hired").values_list('course', flat=True).distinct()
        courses = Course.objects.filter(id__in=courses_keys).all()
        self.fields['class_teaching_course'].queryset = courses

        # Layout of the form
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Common',

                    HTML("""
                    <div class="alert alert-info" role="alert">
                    You should enter a year (under the form of <strong>2 consecutive years - e.g. 2019-2020</strong>), select a term and select an activity type. Based on the activity type you selected, a new tab will be open with further information to provide.
                    </div>
                    """),
                    Field('created_at', type="hidden"),
                    Field('created_by', type="hidden"),
                    Row(
                        Column(Field('year', data_tab="Common", data_required="true"), css_class="form-group col-md-6 mb-0"),
                        Column(Field('term', data_tab="Common", data_required="true"), css_class="form-group col-md-6 mb-0", data_tab="Common", data_required="true"),
                        css_class='form-row'
                    ),
                    InlineRadios('activity_type'),
                    ),
                Tab('Class teaching',
                    Field('class_teaching_course',  data_tab="Class teaching", data_required="true", data_autocomplete="true", data_autocomplete_source=reverse('web:autocomplete_my_courses')),
                    Row(
                        Column(AppendedText('class_teaching_preparation_hours', 'Hr', active=True, data_tab="Class teaching", data_required="false"), css_class="form-group col-md-4 mb-0"),
                        Column(AppendedText('class_teaching_teaching_hours', 'Hr', active=True, data_tab="Class teaching", data_required="false"), css_class="form-group col-md-4 mb-0"),
                        Column(AppendedText('class_teaching_practical_work_hours', 'Hr', active=True, data_tab="Class teaching", data_required="false"), css_class="form-group col-md-4 mb-0"),
                        css_class='form-row'
                    ),
                    ),
                Tab('Master thesis',
                    Field('master_thesis_title',  data_tab="Master thesis", data_required="true"),
                    Field('master_thesis_student_name',  data_tab="Master thesis", data_required="true", data_autocomplete="true", data_autocomplete_source=reverse("web:autocomplete_all_students")),
                    Field('master_thesis_teacher_in_charge',  data_tab="Master thesis", data_required="true", data_autocomplete="true", data_autocomplete_source=reverse("web:autocomplete_all_teachers")),
                    AppendedText('master_thesis_supervision_hours', 'Hr', active=True,  data_tab="Master thesis", data_required="true"),
                    Field('master_thesis_comments',  data_tab="Master thesis", data_required="false"),
                    Row(
                        Column(Field('master_thesis_section',  data_tab="Master thesis", data_required="true"), css_class="form-group col-md-6 mb-0"),
                        Column(Field('master_thesis_other_section',  data_tab="Master thesis", data_required="false"), css_class="form-group col-md-6 mb-0"),
                        css_class='form-row'
                    ),

                    ),

                Tab('Semester project',
                    Field('semester_project_thesis_title', data_tab="Semester project", data_required="true"),
                    Field('semester_project_student_name', data_tab="Semester project", data_required="true", data_autocomplete="true", data_autocomplete_source=reverse("web:autocomplete_all_students")),
                    Field('semester_project_teacher_in_charge', data_tab="Semester project", data_required="true", data_autocomplete="true", data_autocomplete_source=reverse("web:autocomplete_all_teachers")),
                    AppendedText('semester_project_supervision_hours', 'Hr', active=True, data_tab="Semester project", data_required="true"),
                    Field('semester_project_comments', data_tab="Semester project", data_required="false"),
                    ),
                Tab('Other job',
                    Field('other_job_name', data_tab="Other job", data_required="true"),
                    Field('other_job_unit', data_tab="Other job", data_required="true", data_autocomplete="true", data_autocomplete_source=reverse("web:autocomplete_all_units")),
                    Field('other_job_teacher_in_charge', data_tab="Other job", data_required="true", data_autocomplete="true", data_autocomplete_source=reverse("web:autocomplete_all_teachers")),
                    AppendedText('other_job_hours', 'Hr', active=True, data_tab="Other job", data_required="true"),
                    Field('other_job_comments', data_tab="Other job", data_required="false"),
                    ),
                Tab('Nothing to report',
                    Field('nothing_to_report_comments', data_tab="Nothing to report", data_required="true"),

                    ),
                Tab('Not available',
                    Field('not_available_comments', data_tab="Not available", data_required="true"),

                    ),
                Tab('MAN',
                    AppendedText('MAN_hours', 'Hr', active=True, data_tab="MAN", data_required="true"),
                    Field('MAN_comments', data_tab="MAN", data_required="false"),

                    )
            ),
            FormActions(
                Submit('submit', 'Submit'),
                Button('cancel', 'Cancel'),
                Reset('reset', 'Reset')
            ))
