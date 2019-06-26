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
