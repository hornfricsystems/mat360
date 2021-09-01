from django import forms
from mat360admin.models import Mat360SystemUsers
from sacco_manager.models import SaccoRegistrationRequests, Vehicle


class SaccoRequestRegistrationForm(forms.ModelForm):
    class Meta:
        model = SaccoRegistrationRequests
        fields = ('first_name','last_name','id_number','email_address','phone_number','sacco_reg_no','sacco_name')
class VehicleRegistrationForm(forms.ModelForm):
    #Driver_details
    first_name = forms.CharField(max_length=40, required=True, widget=forms.TextInput())
    last_name = forms.CharField(max_length=40, required=True, widget=forms.TextInput())

    id_number = forms.CharField(max_length=8, required=True, widget=forms.TextInput())

    phone_number = forms.CharField(max_length=100, required=True, widget=forms.TextInput())
    email_address = forms.CharField(max_length=100, required=True, widget=forms.TextInput())

    class Meta:
        model=Vehicle
        fields = ('v_number', 'capacity','first_name','last_name','id_number','phone_number','email_address')
class StageControllerRegistrationForm(forms.ModelForm):
    id_number=forms.CharField(max_length=8,required=True,widget=forms.TextInput())
    station = forms.CharField(max_length=40, required=True, widget=forms.TextInput())
    phone_number = forms.CharField(max_length=10, required=True, widget=forms.TextInput())


    class Meta:
        model=Mat360SystemUsers
        fields = ('first_name', 'last_name','email','id_number','phone_number','station')
