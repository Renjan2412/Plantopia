from django import forms
from Catagory.models import Catagory
from store.models import Product,Picture

class ProductForm(forms.ModelForm):
   
    # catagory = forms.ModelChoiceField(queryset=Catagory.objects.all() ,widget=forms.Select(attrs={'class':'form-select'}))
    # product_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control' ,'id':'name'}))
    # images = forms.ImageField(widget=forms.FileInput(attrs={'class':'form-control','id':'formFile',}),required=False)
    # quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control','id':'quantity'}))
    # # selling_price = forms.FloatField(widget=forms.NumberInput(attrs={'class':'form-control','id':'selling_price'}))
    # # original_price = forms.FloatField(widget=forms.NumberInput(attrs={'class':'form-control','id':'original_price'}))
    # description = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','id':'description'}))
    # # status = forms.BooleanField(required=False)
    # is_available = forms.BooleanField(required=False)
    # price = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control','id':'price'}))
    # slug         = forms.SlugField(max_length=200 )
    # stock        = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control','id':'stock'}))
    
    
    class Meta:
        model = Product
        fields = ['catagory','product_name','slug', 'images', 'stock','price', 'description',  'is_available' ]

class ProductImageForm(forms.ModelForm):
    
    class Meta:
        model = Picture
        fields = ['image']