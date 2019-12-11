from django.contrib.auth.models import Group
from django.forms import ModelForm, TextInput
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Reset, Button
from crispy_forms.bootstrap import FormActions, AppendedText, InlineRadios, TabHolder, Tab

from web.models import *

class TimeReportForm(ModelForm):
    class Meta:
        model = TimeReport
        fields = '__all__'
        widgets = {
            'class_teaching_course': TextInput(),
            'master_thesis_teacher_in_charge': TextInput(),
            'semester_project_teacher_in_charge': TextInput(),
            'other_job_teacher_in_charge': TextInput()
        }

    def __init__(self, *args, **kwargs):
        super(TimeReportForm, self).__init__(*args, **kwargs)

        # The below code is commented out because the fields are now rendered as text inputs.
        # It should probably be kept there in case we want to go back to select inputs
        #
        # restrict the dropdown lists to actual teachers
        # teachers = Group.objects.get(name="teachers").user_set.all()
        # self.fields['master_thesis_teacher_in_charge'].queryset = teachers
        # self.fields['semester_project_teacher_in_charge'].queryset = teachers
        # self.fields['other_job_teacher_in_charge'].queryset = teachers

        # Layout of the form
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Common',
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
