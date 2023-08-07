from django import forms


class CouponForm(forms.Form):
    coupon_code = forms.CharField(max_length=100)