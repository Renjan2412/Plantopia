from typing import Any, Dict, Mapping, Optional, Type, Union
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList 
from .models import Account,UserProfile,UserProfileImage

class RegistrationForm(forms.ModelForm) :
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Enter Password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Confirm Password'
    }))
    class Meta:
        model = Account
        fields = ['first_name' , 'last_name' , 'phone_number' , 'email' , 'password']

    def __init__(self , *args ,**kwargs) :
        super(RegistrationForm , self).__init__(*args ,**kwargs) 
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Your Email'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Your Phone Number'
            
        for field in self.fields :
            self.fields[field].widget.attrs['class'] = 'form-group'   


    def clean(self) :
            cleaned_data = super(RegistrationForm ,self).clean()
            password = cleaned_data.get('password')
            confirm_password = cleaned_data.get('confirm_password')

            if password != confirm_password :
                 raise forms.ValidationError(
                      "password does not match !"
                 )  


class UserProfileForm(forms.ModelForm):
    profile_pic = forms.ImageField(required=False,error_messages={'invalid':("Image files only")},widget=forms.FileInput)
    class Meta:
        model  = UserProfileImage
        fields = ('first_name','last_name','profile_pic')

class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('username','phone_number', 'email')                                 
