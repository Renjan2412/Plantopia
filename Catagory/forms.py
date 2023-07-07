from django import forms
from .models import Catagory

# class MyForm(forms.Form):
#     catagory_name = forms.CharField(max_length=60)
#     slug = forms.SlugField(max_length=100)
#     description = forms.CharField(max_length=350, widget=forms.Textarea, required=False)
#     cat_image = forms.ImageField( )
class MyForm(forms.ModelForm):
    class Meta:
        model = Catagory
        fields = '__all__'

class CatagoryForm(forms.ModelForm):
    class Meta:
        model = Catagory
        fields = ['catagory_name', 'slug', 'description', 'cat_image']        
        