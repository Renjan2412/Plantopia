from django.shortcuts import render , get_object_or_404,HttpResponse
from .models import Product
from Catagory.models import Catagory
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q

# Create your views here.

def store(request , catagory_slug = None) :
    catagories = None
    products = None

    if catagory_slug != None :
        catagories = get_object_or_404(Catagory , slug = catagory_slug)
        products = Product.objects.filter(catagory = catagories , is_available = True)
        paginator = Paginator(products , 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else :
         products = Product.objects.all().filter(is_available=True).order_by('id')
         paginator = Paginator(products , 3)
         page = request.GET.get('page')
         paged_products = paginator.get_page(page)
         product_count = products.count()

   
    context = {
        'products' : paged_products,
        'product_count' : product_count,
    }
    return render(request , 'store/store.html' , context)

def product_detail(request , catagory_slug , product_slug) :
    try :
        single_product = Product.objects.get(catagory__slug = catagory_slug , slug = product_slug)

    except Exception as e :
        raise e

    context = {
        'single_product' : single_product , 
    }    
    return render(request , 'store/product-detail.html',context)

def search(request) :
    if 'keyword' in request.GET :
        keyword = request.GET['keyword']
        if keyword :
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()

    context = {
        'products' : products,
        'product_count' : product_count,
        }     
    return render(request , 'store/store.html', context )
   
