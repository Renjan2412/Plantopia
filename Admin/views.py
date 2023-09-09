from django.shortcuts import render,redirect,get_object_or_404
from Catagory.models import Catagory
from accounts.models import Account,Wallet
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
from django.db.models import Count,Q,Sum
from django.db.models.functions import ExtractMonth,ExtractYear
from offer.models import Coupon
from offer.forms import CouponForm
from django.utils import timezone
from datetime import timedelta,datetime,date
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_GET



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
        print("delivered_products :",delivered_products)
        revenue = delivered_products.aggregate(Sum('order__order_total'))['order__order_total__sum'] or 0
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
            print("amount_per_day :",amount_per_day)
            date_list.append(first_date)
            print("date_list :",date_list)
            first_date = first_date + timedelta(days=1)
            print("first_date :",first_date)
    
  
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

@login_required(login_url='admin_signin')
@never_cache
def del_product(request,product_id):
    product_id = request.POST.get('product_id')
    try:
        product = Product.objects.get(id=product_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'Product does not exist...'}, status=404)
    if request.method == 'POST':
        product.delete()
        return JsonResponse({'message': 'Product successfully deleted...'})
    else:
        pass

@login_required(login_url='admin_signin')
@never_cache
def deact_product(request):
    product_id = request.POST.get('product_id')
    product = Product.objects.get(id=product_id)
    if product.is_available:
        product.is_available = False
        product.save()
        return JsonResponse({'title':'Deactivated','message':'Product deactivated...',})
    else:
        product.is_available = True
        product.save()
        return JsonResponse({'title':'Activated','message':'Product Activated...',})    


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
        

@login_required(login_url='admin_signin')
@never_cache
def change_status(request):
    if request.method == "GET":
        orderproduct_id = request.GET['orderproduct_id']
        status = request.GET['status']
        
        orderproduct = OrderProduct.objects.get(id=orderproduct_id)
        if orderproduct.status == 'Return Requested' and status == 'Returned':
            product = orderproduct
            order = orderproduct.order
            order.order_total -= orderproduct.order.order_total
            orderproduct.status = 'Returned'

            wallet = Wallet.objects.get(user_id=orderproduct.order.user.id)
            wallet.balance += orderproduct.order.order_total
            wallet.save()
            
            product.quantity += orderproduct.quantity
            product.save()
            order.save()
            status = 'Returned'

        print('status : ', status)
        orderproduct.status = status
        orderproduct.save()
        return JsonResponse({'message':'Status has been changed..'})  

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