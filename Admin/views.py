from django.shortcuts import render,redirect,get_object_or_404
from Catagory.models import Catagory
from accounts.models import Account
from store.models import Product,Picture
from .forms import ProductForm,ProductImageForm,SearchForm
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.http import JsonResponse
from orders.models import OrderProduct
import calendar
from orders.models import Order
from django.db.models import Count
from django.db.models.functions import ExtractMonth,ExtractYear


# Create your views here.

def my_admin_view(request) :
    delivered_orders = Order.objects.filter(status='Delivered')
    print(delivered_orders)
    delivered_orders_by_months = delivered_orders.annotate(delivered_month=ExtractMonth('created_at')).values('delivered_month').annotate(delivered_count=Count('id')).values('delivered_month', 'delivered_count')
    print( "delivered_orders_by_months")
    print( delivered_orders_by_months)
    delivered_orders_month = []
    delivered_orders_number = []
    for d in delivered_orders_by_months:
         delivered_orders_month.append(calendar.month_name[d['delivered_month']])
         delivered_orders_number.append(list(d.values())[1])

    order_by_months = Order.objects.annotate(month=ExtractMonth('created_at')).values('month').annotate(count=Count('id')).values('month', 'count')
    monthNumber = []
    totalOrders = []

    for o in order_by_months:
        monthNumber.append(calendar.month_name[o['month']])
        totalOrders.append(list(o.values())[1])
        
    order_by_year = Order.objects.annotate(year=ExtractYear('created_at')).values('year').annotate(count=Count('id')).values('year', 'count')

    yearNumber = []
    total_Orders = []

    for o in order_by_year:
        yearNumber.append(o['year'])
        total_Orders.append(o['count'])    

    print(yearNumber)
    print(1)
    
    print(delivered_orders)
    
    print(total_Orders)
    print(order_by_months)
    print(2)
    
    print(delivered_orders_number)
    print(delivered_orders_month)
    print(delivered_orders_by_months)
    context = {
        'monthNumber': monthNumber,
        'totalOrders': totalOrders,
        'yearNumber': yearNumber,
        'total_Orders': total_Orders,
        'delivered_orders':delivered_orders,
        'order_by_months':order_by_months,
        
        'totalOrders':totalOrders,
        'delivered_orders_number':delivered_orders_number,
        'delivered_orders_month':delivered_orders_month,
        'delivered_orders_by_months':delivered_orders_by_months,

    }
    return render(request, "admin-temp/index.html",context)


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
        
def change_status(request, orderproduct_id, new_status):
    order_product = get_object_or_404(OrderProduct, id=orderproduct_id)
    order_product.status = new_status
    order_product.save()
    
    return JsonResponse({'message': 'Status changed successfully'})  

def sales_report(request) :
    if request.user.is_superadmin:
        orders = Order.objects.all().order_by("-created_at")
        print('orders : ', orders)
        msg = 'nothing'
        if request.method == 'POST':
            start_date = request.POST.get('startDate')
            end_date = request.POST.get('endDate')
            if start_date == end_date:
                orders = Order.objects.all().filter(created_at__date=start_date)
                msg = 'Showing the results of the date : '+ start_date
            
            else:
                orders = Order.objects.all().filter(created_at__range=[start_date,end_date])
                msg = 'Showing the results between '+ start_date + '--' + end_date


        context = {
            'orders':orders,
            'msg':msg,
        }

        return render(request,'admin-temp/sales_report.html',context)

def monthly_sales(request):
    if request.user.is_superadmin:
        print('request.post : ', request.POST)
        month = request.POST.get('month')
        orders = Order.objects.all().filter(created_at__month=month)
        print('orders month : ', orders)
        if orders.count() == 0:
            msg = 'No result found for this month'
        else:
            msg = 'The details of the sales in this month are : '
        context = {
            'msg':msg,
            'orders':orders,
        }
        return render(request, 'admin-temp/sales_report.html', context)

      