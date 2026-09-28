from django import forms
from . models import *



class Service_Form(forms.ModelForm):
    class Meta:
        model=Service
        fields='__all__'


