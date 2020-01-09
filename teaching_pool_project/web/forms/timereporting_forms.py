import re

from crispy_forms.bootstrap import (AppendedText, FormActions, InlineRadios,
                                    Tab, TabHolder)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (Button, Column, Field, Layout, Reset, Row,
                                 Submit, Div, HTML)
from django.contrib.auth.models import Group
from django.forms import ModelChoiceField, ModelForm, TextInput
from django.urls import reverse

from web.models import *


class CourseClassChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "{} - {} - {}".format(obj.year, obj.term, obj.subject)


class TimeReportForm(ModelForm):
    class Meta:
        model = TimeReport
        fields = '__all__'
        field_classes = {
            'class_teaching_course': CourseClassChoiceField
        }
        widgets = {
            # 'class_teaching_course': TextInput(),
            'master_thesis_teacher_in_charge': TextInput(),
            'semester_project_teacher_in_charge': TextInput(),
            'other_job_teacher_in_charge': TextInput()
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(TimeReportForm, self).__init__(*args, **kwargs)

        # The below code is commented out because the fields are now rendered as text inputs.
        # It should probably be kept there in case we want to go back to select inputs
        #
        # restrict the dropdown lists to actual teachers
        # teachers = Group.objects.get(name="teachers").user_set.all()
        # self.fields['master_thesis_teacher_in_charge'].queryset = teachers
        # self.fields['semester_project_teacher_in_charge'].queryset = teachers
        # self.fields['other_job_teacher_in_charge'].queryset = teachers

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
                    Row(
                        Column(Field('master_thesis_year',  data_tab="Master thesis", data_required="true"), css_class="form-group col-md-6 mb-0"),
                        Column(Field('master_thesis_term',  data_tab="Master thesis", data_required="true"), css_class="form-group col-md-6 mb-0"),
                        css_class='form-row'
                    ),
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
                    Row(
                        Column(Field('semester_project_year',  data_tab="Semester project", data_required="true"), css_class="form-group col-md-6 mb-0"),
                        Column(Field('semester_project_term', data_tab="Semester project", data_required="true"), css_class="form-group col-md-6 mb-0"),
                        css_class='form-row'
                    ),
                    Field('semester_project_thesis_title', data_tab="Semester project", data_required="true"),
                    Field('semester_project_student_name', data_tab="Semester project", data_required="true", data_autocomplete="true", data_autocomplete_source=reverse("web:autocomplete_all_students")),
                    Field('semester_project_teacher_in_charge', data_tab="Semester project", data_required="true", data_autocomplete="true", data_autocomplete_source=reverse("web:autocomplete_all_teachers")),
                    AppendedText('semester_project_supervision_hours', 'Hr', active=True, data_tab="Semester project", data_required="true"),
                    Field('semester_project_comments', data_tab="Semester project", data_required="false"),
                    ),
                Tab('Other job',
                    Row(
                        Column(Field('other_job_year', data_tab="Other job", data_required="true"), css_class="form-group col-md-6 mb-0"),
                        Column(Field('other_job_term', data_tab="Other job", data_required="true"), css_class="form-group col-md-6 mb-0"),
                        css_class='form-row'
                    ),
                    Field('other_job_name', data_tab="Other job", data_required="true"),
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
                    Row(
                        Column(Field('MAN_year', data_tab="MAN", data_required="true"), css_class="form-group col-md-6 mb-0"),
                        Column(Field('MAN_term', data_tab="MAN", data_required="true"), css_class="form-group col-md-6 mb-0"),
                        css_class='form-row'
                    ),
                    AppendedText('MAN_hours', 'Hr', active=True, data_tab="MAN", data_required="true"),
                    Field('MAN_comments', data_tab="MAN", data_required="false"),

                    )
            ),
            FormActions(
                Submit('submit', 'Submit'),
                Button('cancel', 'Cancel'),
                Reset('reset', 'Reset')
            ))

    def clean(self):
        cleaned_data = super().clean()

        # validate the common fields
        year_raw_value = cleaned_data.get('year')
        pattern = r'(?P<year1>\d{4})-(?P<year2>\d{4})'
        p = re.compile(pattern)

        if not p.match(year_raw_value):
            self.add_error('year', "The year should be under the form of two consecutive years (e.g. 2019-2020)")
        else:
            m = p.search(year_raw_value)
            year1 = int(m.group('year1'))
            year2 = int(m.group('year2'))
            if year2 != (year1+1):
                self.add_error('year', "The year should be under the form of two consecutive years (e.g. 2019-2020)")

        activity_type = cleaned_data.get('activity_type')

        if activity_type == 'class teaching':
            if not cleaned_data.get('class_teaching_course'):
                msg = "When selecting a 'class teaching' activity, a course should be selected"
                self.add_error('activity_type', msg)
                self.add_error('class_teaching_course', msg)

            if cleaned_data.get('class_teaching_preparation_hours') is None:
                msg = "When selecting a 'class teaching' activity, the preparation hours must have a value"
                self.add_error('class_teaching_preparation_hours', msg)
                self.add_error('activity_type', msg)

            if cleaned_data.get('class_teaching_teaching_hours') is None:
                msg = "When selecting a 'class teaching' activity, the teaching hours must have a value"
                self.add_error('class_teaching_teaching_hours', msg)
                self.add_error('activity_type', msg)

            if cleaned_data.get('class_teaching_practical_work_hours') is None:
                msg = "When selecting a 'class teaching' activity, the practical work hours must have a value"
                self.add_error('class_teaching_practical_work_hours', msg)
                self.add_error('activity_type', msg)

            if cleaned_data.get('class_teaching_preparation_hours') == 0 and cleaned_data.get('class_teaching_teaching_hours') == 0 and cleaned_data.get('class_teaching_practical_work_hours') == 0:
                msg = "At least one of the number of hours (preparation, teaching or practical work hours) should have a value above 0"
                self.add_error('class_teaching_preparation_hours', msg)
                self.add_error('class_teaching_teaching_hours', msg)
                self.add_error('class_teaching_practical_work_hours', msg)

            # clean up the year and the term with data from the selected course
            self.cleaned_data['year'] = cleaned_data.get('class_teaching_course').year
            self.instance.year = cleaned_data.get('class_teaching_course').year
            french_term = cleaned_data.get('class_teaching_course').term
            if french_term == "ETE":
                english_term = "summer"
            elif french_term == "HIVER":
                english_term = "winter"
            else:
                english_term = self.cleaned_data['term']
            self.cleaned_data['term'] = english_term
            self.instance.year = english_term

            # Remove the data from possibly other data


        # time to go back
        return self.cleaned_data
