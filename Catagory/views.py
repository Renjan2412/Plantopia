from django.shortcuts import render,redirect,get_object_or_404
from .forms import MyForm
from .models import Catagory
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import CatagoryForm



# Create your views here.

# def my_view(request) :
#      # form = MyForm()
#      return render(request,'admin-temp/catagory.html' )

def my_admin_category(request):
    cate= Catagory.objects.all()
    context = {
        'cate':cate,
        
    }

    return render(request,'admin-temp/catagory.html',context)

def catagory_add(request) :
    if request.method == 'POST' :
        catagory_name = request.POST.get('catagory_name')
        catagory_slug = request.POST.get('catagory_slug')
        catagory_description = request.POST.get('catagory_description')
        catagory_image = request.FILES.get('catagory_image')
        # print('request.POST :',request.POST)
        # print('request.FILES :',request.FILES)
        # print('catagory_image :',catagory_image)
        
        catagory = Catagory(
             catagory_name = catagory_name ,
             slug = catagory_slug ,
             description = catagory_description ,
             cat_image = catagory_image,
         )

        catagory.save()
        return redirect('my_admin_category')
    else :
        return render(request,'admin-temp/catagory-add.html')
    
@never_cache
@login_required(login_url='user_login')
def update_catagory(request , id):
    if request.user.is_superadmin:
        catagory = get_object_or_404(Catagory, id=id)
        if request.method == "POST":
            form = CatagoryForm(request.POST, request.FILES, instance=catagory)
            if form.is_valid():
                catagory = form.save()
                return redirect('my_admin_category')
        else:
            form = CatagoryForm(instance = catagory)
        return render(request, "admin-temp/update_catagory.html",{'form':form})
@never_cache
@login_required(login_url='user_login')
def delete_category(request, id):
    if request.user.is_superadmin:
        get_object_or_404(Catagory, id=id).delete()
    return redirect('my_admin_category')    

     
    
    

    
