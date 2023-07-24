
from django import forms
from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['first_name', 'last_name', 'address_line_1', 'address_line_2', 'email', 'city', 'state', 'country', 'phone_number', 'post_code', 'order_note']
