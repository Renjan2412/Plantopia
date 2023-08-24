from django import forms
from .models import Coupon


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ('code', 'valid_from', 'valid_to', 'min_amount', 'discount_amount')
        widgets = {
            'code':forms.TextInput(attrs={'class':'form-control'}),
            'valid_from':forms.DateTimeInput(attrs={'type':'datetime-local', 'class':'form-control'}),
            'valid_to':forms.DateTimeInput(attrs={'type':'datetime-local', 'class':'form-control'}),
            'min_amount':forms.NumberInput(attrs={'class':'form-control'}),
            'discount_amount':forms.NumberInput(attrs={'class':'form-control'}),
        }