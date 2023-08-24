from django.shortcuts import render , get_object_or_404,HttpResponse
from .models import Product,Wishlist
from Catagory.models import Catagory
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from carts.models import CartItem
from django.http import JsonResponse



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

def search(request):
    products = []
    product_count = 0

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']  # Define 'keyword' before printing it
        print('keyword:', keyword)  # Now it's safe to print

        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
        
        print('products:', products)
        print('product_count:', product_count)    

    context = {
        'products': products,
        'product_count': product_count,
    }     
    return render(request, 'store/store.html', context)

# def search_suggestions(request) :
#     if 'term' in request.GET :
#         term = request.GET['term']
#         suggestions = []

#         # fetching suggestions based on the term from the product model
#         products = Product.objects.filter(
#             Q(description__icontains=term) | Q(product_name__icontains=term)
#         ).values_list('product_name', flat=True) 

#         suggestions = [product_name for product_name in products]

#         return JsonResponse({'suggestions': suggestions} , safe=False)

@login_required(login_url='user_login')
def wishlist(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    cart_items = CartItem.objects.filter(user=request.user)
    # variations = cart_items.values_list('product_variation', flat=True).distinct()
    # print('variations : ', variations)
    # wishlist_count = wishlist.count()
    
    context = {
        'wishlist':wishlist,
        'cart_items':cart_items,
        # 'wishlist_count':wishlist_count,
    }
    return render(request, 'store/wishlist.html', context)


def add_to_wishlist(request):
    current_user = request.user
    # flavour = request.POST.get('flavour')
    # weight  = request.POST.get('weight')
    product_id = request.POST.get('product_id')
    print(product_id)
    
    
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        is_wishlist_exists = Wishlist.objects.filter(product=product, user=current_user).exists()
        if is_wishlist_exists:
            return JsonResponse({'message':'Item already in the Wishlist...'})
        else:
            print('item is not in wishlist')
            wishlist = Wishlist.objects.create(
                product=product,
                user=current_user,
            )
            wishlist.save()
            print(wishlist)
            return JsonResponse({'message':'Product successfully added to wishlist'})
    return JsonResponse({'message':'success'})

# Delete wishlist item

def del_wishlist_item(request):
    wishlist_item_id = request.POST.get('wishlist_item_id')
    item = Wishlist.objects.get(id=wishlist_item_id)
    item.delete()
    return JsonResponse({'message':'item deleted from wishlist...'})
   
