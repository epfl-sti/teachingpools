import re

from django import forms
from django.db.models.functions import Lower
from django.forms import HiddenInput, ModelForm
from django.forms.widgets import SelectMultiple, Textarea

from web.models import *


class NameForm(forms.Form):
    your_name = forms.CharField(label="Your name", max_length=100)


class RequestForTA(forms.ModelForm):
    class Meta:
        model = NumberOfTAUpdateRequest
        fields = ("requestedNumberOfTAs", "requestReason")
        widgets = {
            "requestReason": Textarea(),
        }
        labels = {
            "requestReason": "Reason",
        }
        help_texts = {
            "requestReason": "Optionally, you can provide a reason for this request",
        }


class RequestForTAApproval(forms.Form):
    request_id = forms.IntegerField(widget=forms.HiddenInput)
    opened_at = forms.DateTimeField(disabled=True, required=False)
    requester = forms.CharField(disabled=True, required=False)
    course = forms.CharField(disabled=True, required=False)
    requestedNumberOfTAs = forms.IntegerField(
        disabled=True, label="Requested number of TAs", required=False
    )
    reason_for_request = forms.CharField(
        disabled=True, widget=forms.Textarea, required=False
    )
    reason_for_decision = forms.CharField(widget=forms.Textarea, required=False)


class RequestForTAView(forms.Form):
    request_id = forms.IntegerField(widget=forms.HiddenInput)
    opened_at = forms.DateTimeField(disabled=True, required=False)
    requester = forms.CharField(disabled=True, required=False)
    course = forms.CharField(disabled=True, required=False)
    requestedNumberOfTAs = forms.IntegerField(
        disabled=True, label="Requested number of TAs", required=False
    )
    reason_for_request = forms.CharField(
        disabled=True, widget=forms.Textarea, required=False
    )
    status = forms.CharField(disabled=True, required=False)
    reason_for_decision = forms.CharField(
        widget=forms.Textarea, required=False, disabled=True
    )


class AvailabilityForm(ModelForm):
    class Meta:
        model = Availability
        fields = "__all__"
        widgets = {
            "year": forms.HiddenInput(),
            "person": forms.HiddenInput(),
            "term": forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        availability = cleaned_data["availability"].lower()
        reason = cleaned_data["reason"]
        if availability == "unavailable" and not reason:
            msg = "A reason should be provided when you say you will be unavailable."
            self.add_error("reason", msg)


class ApplicationForm_phd(ModelForm):
    class Meta:
        model = Applications
        fields = ["applicant", "course"]
        widgets = {"applicant": forms.HiddenInput(), "course": forms.HiddenInput()}


class ApplicationForm_teacher(ModelForm):
    class Meta:
        model = Applications
        fields = "__all__"
        exclude = ["openedAt", "status", "closedAt", "closedBy"]
        labels = {
            "applicant": "PhD",
            "decisionReason": "Reason for decision",
        }
        widgets = {
            "applicant": forms.HiddenInput(),
            "course": forms.HiddenInput(),
        }


class LanguagesForm(forms.Form):
    OPTIONS = (("f", "French"), ("e", "English"), ("g", "German"))
    languages = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, choices=OPTIONS
    )

    def clean(self):
        cleaned_data = super().clean()
        possible_choices = [item[0] for item in self.fields["languages"].choices]
        if "languages" in cleaned_data:
            for language in cleaned_data["languages"]:
                if language not in possible_choices:
                    self.add_error(
                        "languages",
                        "The value provided is not part of the available choices.",
                    )
        else:
            self.add_error(
                "languages", "You should be able to teach at least in one language"
            )


class TopicForm(ModelForm):
    class Meta:
        model = Person
        fields = ("topics",)

    def __init__(self, *args, **kwargs):
        super(TopicForm, self).__init__(*args, **kwargs)

        self.fields["topics"].widget = SelectMultiple(attrs={"size": 20})
        self.fields["topics"].queryset = Topic.objects.order_by(Lower("name")).all()
        self.fields[
            "topics"
        ].help_text = "Don't forget to hold the CTRL key (or cmd on a Mac) to select multiple topics"


class ConfigForm(ModelForm):
    class Meta:
        model = Config
        fields = "__all__"


class PeopleManagementForm(forms.Form):
    add_person = forms.CharField(max_length=255)

    class Meta:
        labels = {
            "add_person": "SCIPER or username",
        }

    def __init__(self, *args, **kwargs):
        super(PeopleManagementForm, self).__init__(*args, **kwargs)

        self.fields["add_person"].label = "Name or sciper"
        self.fields[
            "add_person"
        ].help_text = "You can search the person by sciper or by name"

    def clean(self):
        cleaned_data = super().clean()
        pattern = r".*,\s.*\((\d*)\)"
        if not re.match(pattern, cleaned_data["add_person"]):
            self.add_error(
                "add_person",
                "The value passed is not correct. It should be <last name>, <first name> (<sciper>)",
            )


class AssignmentManagementForm(forms.Form):
    person = forms.CharField(max_length=255)
    course = forms.CharField(max_length=255)

    class Meta:
        labels = {
            "person": "SCIPER or username",
            "course": "course code or subject",
            "role": "Role",
        }

    def __init__(self, *args, **kwargs):
        super(AssignmentManagementForm, self).__init__(*args, **kwargs)

        self.fields["person"].label = "Name or sciper"
        self.fields[
            "person"
        ].help_text = "You can search the person by sciper or by name"
        self.fields["course"].label = "Code or subject"
        self.fields["course"].help_text = "You can search the course by code or subject"

    def clean(self):
        cleaned_data = super().clean()
        person_pattern = r".*,\s.*\((\d*)\)"
        if not re.match(person_pattern, cleaned_data["person"]):
            self.add_error(
                "person",
                "The value passed is not correct. It should be <last name>, <first name> (<sciper>)",
            )
        course_pattern = r"^.*\s\(.*\)$"
        if not re.match(course_pattern, cleaned_data["course"]):
            self.add_error(
                "course",
                "The value passed is not correct. It should be <subject>(<code>)",
            )

