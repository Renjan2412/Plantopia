from django.shortcuts import render,redirect,get_object_or_404
from Catagory.models import Catagory
from accounts.models import Account
from django.contrib import messages
from store.models import Product,Picture
from .forms import ProductForm,ProductImageForm,SearchForm
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.forms import inlineformset_factory
from django.http import JsonResponse
from orders.models import OrderProduct
import calendar
from orders.models import Order
from django.db.models import Count,Q
from django.db.models.functions import ExtractMonth,ExtractYear
from offer.models import Coupon
from offer.forms import CouponForm
from django.utils import timezone
from datetime import timedelta,datetime,date



# Create your views here.

def admin_signin(request) :
    if request.user.is_superuser:
        return redirect('my_admin_view')
    if request.method == "POST":
            print('request POST :', request.POST)
            email = request.POST.get('email')
            passw = request.POST.get('password')
            user = authenticate(email=email,password=passw)
            print('user : ',user)
            if user is not None and user.is_superuser:
                login(request, user)
                return redirect('my_admin_view') 
            else:
                messages.error(request, 'Invalid credentails...')
    return render(request,'admin-temp/admin_signup.html')

def my_admin_view(request) :
    if request.user.is_superuser:
        user_count = Account.objects.filter(is_superuser=False).count()
        delivered_products = OrderProduct.objects.all().filter(status='Delivered')
        revenue = sum(product.total() for product in delivered_products)
        print('revenue:',revenue)
        total_orders = OrderProduct.objects.all().count()
        status_counts = OrderProduct.objects.values('status').annotate(count=Count('status'))
        product_count = Product.objects.all().count()
        category_count = Catagory.objects.all().count()
        current_year = timezone.now().year
        order_detail = OrderProduct.objects
        monthly_order_count = []
        month = timezone.now().month
        order_detail = OrderProduct.objects.filter(
            order__updated_at__lt=date(current_year, 12, 31),
            status='Delivered',
        )

        for i in range(1, month + 1):
            monthly_order = order_detail.filter(order__updated_at__month=i).count()
            monthly_order_count.append(monthly_order)


        today = datetime.now()
        neworders = OrderProduct.objects.filter(order__updated_at__month=today.month).values('order__updated_at__date').annotate(orderitemscount=Count('id', filter=Q(status='Order Placed')))
        cancelledorders = OrderProduct.objects.filter(order__updated_at__month=today.month).values('order__updated_at__date').annotate(cancelleditemscount=Count('id',filter=Q(status='Cancelled')))
        returnorders = OrderProduct.objects.filter(order__updated_at__month=today.month).values('order__updated_at__date').annotate(returnedorderscount=Count('id', filter=Q(status='Returned')))
        deliveredorders = OrderProduct.objects.filter(order__updated_at__month=today.month).values('order__updated_at__date').annotate(delivereditemscount=Count('id', filter=Q(status='Delivered')))

        orderitems = OrderProduct.objects.filter(status='Delivered')
        last_date = datetime.now().date()
        first_date = last_date - timedelta(days=6)
        amount_per_day = []
        date_list = []
        for i in range(1,8):
            total_amount_per_day = 0
            for order in orderitems:
                if order.order.updated_at.date() == first_date:
                    total_amount_per_day += order.total()
            amount_per_day.append(total_amount_per_day)
            date_list.append(first_date)
            first_date = first_date + timedelta(days=1)
    
  
        context = {
            'revenue':revenue,
            'total_orders':total_orders,
            'status_counts':status_counts,
            'product_count':product_count,
            'category_count':category_count,
            'user_count':user_count,
            'amount_per_day':amount_per_day,
            'date_list':date_list,
            'neworders':neworders,
            'cancelledorders':cancelledorders,
            'returnorders':returnorders,
            'deliveredorders':deliveredorders,
            'monthly_order_count':monthly_order_count,

        }
        return render(request,'admin-temp/index.html', context)
    return redirect('admin_signin')
    # delivered_orders = Order.objects.filter(status='Delivered')
    # print(delivered_orders)
    # delivered_orders_by_months = delivered_orders.annotate(delivered_month=ExtractMonth('created_at')).values('delivered_month').annotate(delivered_count=Count('id')).values('delivered_month', 'delivered_count')
    # print( "delivered_orders_by_months")
    # print( delivered_orders_by_months)
    # delivered_orders_month = []
    # delivered_orders_number = []
    # for d in delivered_orders_by_months:
    #      delivered_orders_month.append(calendar.month_name[d['delivered_month']])
    #      delivered_orders_number.append(list(d.values())[1])

    # order_by_months = Order.objects.annotate(month=ExtractMonth('created_at')).values('month').annotate(count=Count('id')).values('month', 'count')
    # monthNumber = []
    # totalOrders = []

    # for o in order_by_months:
    #     monthNumber.append(calendar.month_name[o['month']])
    #     totalOrders.append(list(o.values())[1])
        
    # order_by_year = Order.objects.annotate(year=ExtractYear('created_at')).values('year').annotate(count=Count('id')).values('year', 'count')

    # yearNumber = []
    # total_Orders = []

    # for o in order_by_year:
    #     yearNumber.append(o['year'])
    #     total_Orders.append(o['count'])    

    # print(yearNumber)
    # print(1)
    
    # print(delivered_orders)
    
    # print(total_Orders)
    # print(order_by_months)
    # print(2)
    
    # print(delivered_orders_number)
    # print(delivered_orders_month)
    # print(delivered_orders_by_months)
    # context = {
    #     'monthNumber': monthNumber,
    #     'totalOrders': totalOrders,
    #     'yearNumber': yearNumber,
    #     'total_Orders': total_Orders,
    #     'delivered_orders':delivered_orders,
    #     'order_by_months':order_by_months,
        
    #     'totalOrders':totalOrders,
    #     'delivered_orders_number':delivered_orders_number,
    #     'delivered_orders_month':delivered_orders_month,
    #     'delivered_orders_by_months':delivered_orders_by_months,

    # }
    # return render(request, "admin-temp/index.html",context)

@login_required(login_url='admin_signin')
@never_cache
def ad_logout(reuqest):
    logout(reuqest)
    return redirect('admin_signin')


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
    
    if request.user.is_superuser :
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
    if request.user.is_superuser :
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
    if request.user.is_superuser:
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
    if request.user.is_superuser:
        orders = Order.objects.all().order_by("-updated_at")
        print('orders : ', orders)
        msg = 'nothing'
        if request.method == 'POST':
            start_date = request.POST.get('startDate')
            end_date = request.POST.get('endDate')
            if start_date == end_date:
                orders = Order.objects.all().filter(updated_at__date=start_date)
                msg = 'Showing the results of the date : '+ start_date
            
            else:
                orders = Order.objects.all().filter(updated_at__range=[start_date,end_date])
                msg = 'Showing the results between '+ start_date + '--' + end_date


        context = {
            'orders':orders,
            'msg':msg,
        }

        return render(request,'admin-temp/sales_report.html',context)

def monthly_sales(request):
    if request.user.is_superuser:
        print('request.post : ', request.POST)
        month = request.POST.get('month')
        orders = Order.objects.all().filter(updated_at__month=month)
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
    
@login_required(login_url='admin_signin')
@never_cache
def coupons(request):
    coupons = Coupon.objects.all()
    context = {
        'coupons':coupons,
    }
    return render(request, 'admin-temp/coupon.html', context)    

@login_required(login_url='admin_signin')
@never_cache
def add_coupon(request, coupon_id=0):
    if coupon_id == 0:
        if request.method == "POST":
            form = CouponForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('coupons')
        form = CouponForm()
    else:
        coupon = Coupon.objects.get(id=coupon_id)
        if request.method == 'POST':
            form = CouponForm(request.POST, instance=coupon)
            if form.is_valid():
                form.save()
                return redirect('coupons')
        form = CouponForm(instance=coupon)
    context = {
        'form':form,
    }
    return render(request, 'admin-temp/add_coupon.html', context)   

@login_required(login_url='admin_signin')
@never_cache
def del_coupon(request):
    print('del coupon is workinggg')
    coupon_id = request.POST.get('coupon_id')
    coupon = Coupon.objects.get(id=coupon_id)
    coupon.delete()
    return JsonResponse({'message':'Coupon deleted successfully...'})  

@login_required(login_url='admin_signin')
@never_cache
def deact_coupon(request):
    coupon_id = request.POST.get('coupon_id')
    coupon = Coupon.objects.get(id=coupon_id)
    if coupon.active:
        coupon.active = False
        coupon.save()
        return JsonResponse({'title':'Deactivated', 'message':'coupon deactivated...'})
    else:
        coupon.active = True
        coupon.save()
        return JsonResponse({'title':'Activated','message':'coupon activated...'})