from django.shortcuts import render,redirect
from Catagory.models import Catagory
from accounts.models import Account
from store.models import Product,Picture
from .forms import ProductForm,ProductImageForm
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory

# Create your views here.

def my_admin_view(request) :
    return render(request , 'admin-temp/index.html')

# User side

def users_list(request) :
    users = Account.objects.all()
    context = {
        'users' : users
    }
    return render(request, 'admin-temp/users-list.html' , context)

def block_user(request,id):
    if request.user.is_superadmin:
        user = Account.objects.get(pk=id)
        if user.is_blocked:
            user.is_blocked=False
            user.save()
            return redirect('users-list')
        else:
            user.is_blocked = True
            user.save()
            return redirect('users-list')
    return redirect('users-list')


# product side

def product_listt(request):
    products = Product.objects.all()
    

    context = {
        'products' : products
    }
    
    return render(request , 'store/product_list.html',context)

ImageFormSet = ProductImageFormSet = inlineformset_factory(Product, Picture, form=ProductImageForm, extra=5)
@never_cache
@login_required(login_url='user_login')
def add_product(request) :
    
    if request.user.is_superadmin :
        if request.method == 'POST' :
            form = ProductForm(request.POST, request.FILES)
            images = request.FILES.getlist('images')

            if form.is_valid() :
                form.save()
                # try :
                #     product = form.save(commit=False)
                #     product.save()

                #     for img in images :
                #         new_image = Picture(product=product, image = img)
                #         new_image.save()
                # except Exception as e :
                #     print(e)

                return redirect(product_listt)
        else :
            form = ProductForm()                
    return render(request,'admin-temp/add_product.html',{'form' : form} )