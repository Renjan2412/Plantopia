from django.shortcuts import render,redirect,get_object_or_404
from Catagory.models import Catagory
from accounts.models import Account
from store.models import Product,Picture
from .forms import ProductForm,ProductImageForm,SearchForm
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.http import JsonResponse

# Create your views here.

def my_admin_view(request) :
    return render(request , 'admin-temp/index.html')

# User side

def users_list(request) :
    users = Account.objects.all().order_by('id')
    context = {
        'users' : users
    }
    return render(request, 'admin-temp/users-list.html' , context)

# def block_user(request,id):
#     if request.user.is_superadmin:
#         user = Account.objects.get(pk=id)
#         if user.is_blocked:
#             user.is_blocked=False
#             user.save()
#             return redirect('users-list')
#         else:
#             user.is_blocked = True
#             user.save()
#             return redirect('users-list')
#     return redirect('users-list')


# product side

def product_listt(request):
    products = Product.objects.all()
    

    context = {
        'products' : products
    }
    
    return render(request , 'store/product_list.html',context)

ImageFormSet = ProductImageFormSet = inlineformset_factory(Product, Picture, form=ProductImageForm)
@never_cache
@login_required(login_url='user_login')
def add_product(request) :
    
    if request.user.is_superadmin :
        if request.method == 'POST' :
            form = ProductForm(request.POST, request.FILES)
            images = request.FILES.getlist('images')

            if form.is_valid() :
                # form.save()
                try :
                    product = form.save(commit=False)
                    product.save()

                    for img in images :
                        new_image = Picture(product=product, image = img)
                        new_image.save()
                except Exception as e :
                    print(e)

                return redirect(product_listt)
        else :
            form = ProductForm()                
    return render(request,'admin-temp/add_product.html',{'form' : form} )

@never_cache
def update_product(request,id):
    if request.user.is_superadmin :
        product = get_object_or_404(Product, id= id)
        print(product)
        image_form = ImageFormSet(request.POST or None, request.FILES or None, instance=product)
        print(image_form)
        if request.method == "POST":
            print("1")
            form = ProductForm(request.POST, request.FILES, instance=product)
            print("2")
            if form.is_valid() and image_form.is_valid():
                print("4")
                product = form.save()
                image_form.save()
                print("3")
                return redirect('product_listt')
        else:
            form = ProductForm(instance=product)
    
        return render(request, 'admin-temp/update-product.html', {'form': form, 'image_form':image_form})

@never_cache
@login_required(login_url='user_login')
def delete_product(request, id):
    get_object_or_404(Product, id=id).delete()
    return redirect('product_listt')

def search(request) :
    search_query = request.GET.get('search_query', '')
    results = []

    if request.user.is_superuser :
        if search_query :
            results = Product.objects.filter(product_name__icontains =search_query)
    else :
        if search_query :
            results = Product.objects.filter(product_name__icontains=search_query, is_available=True)        

    context = {
        'search_query' : search_query,
        'results' : results,
    }
    return render(request, 'search.html' , context)    



# ajax block

def block_user(request,id):
    if request.user.is_superadmin:
        user = Account.objects.get(pk=id)
        if user.is_blocked:
            user.is_blocked=False
            user.save()
            return JsonResponse({'title':'Unblocked','text':'User is Unblocked'})   
        else:
            user.is_blocked = True
            user.save()
            return JsonResponse({'title':'Blocked','text':'User is Blocked'})