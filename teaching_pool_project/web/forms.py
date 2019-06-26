from django import forms
from django.forms import HiddenInput, ModelForm

from web.models import *


class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)


class RequestForTA(forms.Form):
    course_id = forms.IntegerField(widget=forms.HiddenInput)
    number_of_TAs = forms.IntegerField(
        max_value=100, min_value=0, label="Number of requested TAs")
    reason = forms.CharField(widget=forms.Textarea, required=False)


class RequestForTAApproval(forms.Form):
    request_id = forms.IntegerField(widget=forms.HiddenInput)
    opened_at = forms.DateTimeField(disabled=True, required=False)
    requester = forms.CharField(disabled=True, required=False)
    course = forms.CharField(disabled=True, required=False)
    requestedNumberOfTAs = forms.IntegerField(
        disabled=True, label='Requested number of TAs', required=False)
    reason_for_request = forms.CharField(
        disabled=True, widget=forms.Textarea, required=False)
    reason_for_decision = forms.CharField(
        widget=forms.Textarea, required=False)


class RequestForTAView(forms.Form):
    request_id = forms.IntegerField(widget=forms.HiddenInput)
    opened_at = forms.DateTimeField(disabled=True, required=False)
    requester = forms.CharField(disabled=True, required=False)
    course = forms.CharField(disabled=True, required=False)
    requestedNumberOfTAs = forms.IntegerField(
        disabled=True, label='Requested number of TAs', required=False)
    reason_for_request = forms.CharField(
        disabled=True, widget=forms.Textarea, required=False)
    reason_for_decision = forms.CharField(
        widget=forms.Textarea, required=False, disabled=True)


class AvailabilityForm(ModelForm):
    class Meta:
        model = Availability
        fields = '__all__'
        widgets = {
            'year': forms.HiddenInput(),
            'person': forms.HiddenInput()
        }

    def clean(self):
        cleaned_data = super().clean()
        availability = cleaned_data['availability'].lower()
        reason = cleaned_data['reason']
        if availability == "unavailable" and not reason:
            msg = 'A reason should be provided when you say you will be unavailable.'
            self.add_error('reason', msg)


class LanguagesForm(forms.Form):
    OPTIONS = (
        ('f', 'French'),
        ('e', 'English'),
        ('g', 'German')
    )
    languages = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, choices=OPTIONS)

    def clean(self):
        cleaned_data = super().clean()
        possible_choices = [item[0] for item in self.fields['languages'].choices]
        if 'languages' in cleaned_data:
            for language in cleaned_data['languages']:
                if language not in possible_choices:
                    self.add_error(
                        'languages', 'The value provided is not part of the available choices.')
        else:
            self.add_error(
                'languages', "You should be able to teach at least in one language")
