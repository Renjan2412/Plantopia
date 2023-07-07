from django import forms
from Catagory.models import Catagory
from store.models import Product,Picture




class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'slug', 'description', 'price', 'images', 'stock', 'is_available', 'catagory']
        
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'images': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'catagory': forms.Select(attrs={'class': 'form-select'}),
        }

class ProductImageForm(forms.ModelForm):
    
    class Meta:
        model = Picture
        fields = ['image']

class SearchForm(forms.Form) :
    search_query = forms.CharField(max_length=100, required=False, label='')
