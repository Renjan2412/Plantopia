from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from .forms import RegistrationForm,UserForm,UserProfileForm
from .models import Account , UserProfile,Wallet,UserProfileImage
from django.contrib import messages,auth
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from .verify import send,check
from store.models import Product
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from carts.views import _cart_id
from carts.models import Cart,CartItem,Address
from carts.forms import AddressForm
import requests,logging
from urllib.parse import urlparse, parse_qs
from orders.models import Order,OrderProduct
from store .models import Wishlist
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

#download invoice

from io import BytesIO
from xhtml2pdf import pisa
from django.views.generic import View
from django.template.loader import get_template

# Create your views here.


def home(request):
    sort_option = request.GET.get('sort_option', 'Default')

    if sort_option == 'Name, A to Z':
        products = Product.objects.filter(is_available=True).order_by('product_name')
    elif sort_option == 'Name, Z to A':
        products = Product.objects.filter(is_available=True).order_by('-product_name')
    elif sort_option == 'Price, Low to High':
        products = Product.objects.filter(is_available=True).order_by('price')
    elif sort_option == 'Price, High to Low':
        products = Product.objects.filter(is_available=True).order_by('-price')
    else:
        products = Product.objects.filter(is_available=True)
        
    sliced_products = products[:4]

      

    context = {
        'products': sliced_products,
        'sort_option': sort_option,
        
    }
    return render(request, 'home.html', context)

def register(request) :
    if request.method == 'POST' :
        form = RegistrationForm(request.POST)
        if form.is_valid() :
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name'] 
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password'] 
            username = email.split("@")[0]


            user = Account.objects.create_user(first_name=first_name , last_name=last_name , email=email , username=username , password=password)  
            user.phone_number = phone_number
            user.save()
            messages.success(request , 'Registration Successful')
            return redirect('register')
    else :
         form = RegistrationForm()

    context = {
        'form' : form,
    }
    return render(request,'accounts/register.html' , context)

def user_login(request) :
    if request.method == 'POST' :
        email = request.POST['email']
        password = request.POST['password']
        

        user = auth.authenticate(email=email , password=password)

        if user is not None :
            try :
                cart = Cart.objects.get(cart_id=_cart_id)
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists :
                    cart_item = CartItem.objects.filter(cart=cart)

                    for item in cart_item :
                        item.user = user
                        item.save()

            except :
                pass    
            auth.login(request , user)
            messages.success(request, 'You Are Now Logged IN')
            url = request.META.get('HTTP_REFERER')
            if url is None:
                return redirect('dashboard')

            try:
                parsed_url = urlparse(url)
                query = parsed_url.query  
                params = parse_qs(query)
                if 'next' in params:
                    nextPage = params['next'][0]
                    return redirect(nextPage)
            except Exception as e:
                logging.error(f'Error occurred: {e}')
            return redirect('dashboard')
        
        else :
            messages.error(request , 'Invalid Login Credential')
      
            print('else is workinggg')
            return redirect('user_login')
        
    return render(request,'accounts/user_login.html')

def login_otp(request) :
     if request.user.is_authenticated:
        print('1')
        return redirect('home')
     if request.method == 'POST':
        print('11')
        phone_number = request.POST['phone_number']
        # if not re.match(r'^[0-9]+$',phone_number):
        #     messages.error(request,'Phone number should contain only digits')
        # if len(phone_number)<10:
        #     messages.error(request,'Please provide a valid Phone number')
        if Account.objects.all().filter(phone_number=phone_number):
            print('111')
            phone_number_with_country_code='+91'+phone_number
            send(phone_number_with_country_code)
            return redirect(login_otp_verify,phone_number)
        else:
            messages.error(request,'Phone number is not registered with us')
            
     return render(request,'accounts/login_otp.html')


def login_otp_verify(request , phone_number) :
     if request.user.is_authenticated:
        return redirect('home')
     if request.method == 'POST':
        otp_code = request.POST['otp']
        phone_number_with_country_code = '+91'+phone_number
        if check(phone_number_with_country_code,otp_code):
            user = Account.objects.all().get(phone_number=phone_number)
            if user.is_blocked:
                messages.warning(request,'You are Blocked by admin.please contact for further info')
                return redirect('accounts/login_otp')
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Incorrect OTP')

     return render(request,'accounts/login_otp_varify.html')

@login_required(login_url = 'user_login')
def logout(request) :
    auth.logout(request)
    messages.success(request, 'You Are Logged Out')

    return redirect('user_login')

@login_required(login_url = 'user_login')
def dashboard(request) :
    orders = Order.objects.order_by('-updated_at').filter(user_id=request.user.id)
    userprofile = UserProfileImage.objects.get(user=request.user)    
    order_count = orders.count()
    try :
        wallet_amount = Wallet.objects.get(user_id = request.user.id).balance
    except ObjectDoesNotExist:
            wallet_amount = 0.00
    context = {       
        'order_count':order_count,
        'user_profile':userprofile,
        'wallet_amount':wallet_amount,
    }
    return render(request , 'accounts/dashboard.html',context)



def forgotPassword(request) :
    if request.method == 'POST' :
        email = request.POST['email']
        if Account.objects.filter(email=email).exists() :
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = "Reset Your Password"
            message= render_to_string('accounts/reset_password_email.html',{
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()

            messages.success(request,'Password reset email has send to Your Email Address..')
            return redirect('user_login')    
        else :
            messages.error(request, 'Account Does not Exist')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')

def resetPassword_validate(request) :
    return HttpResponse("ok")

@login_required
def edit_profile(request) :
    user_profile, created = UserProfileImage.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        # userprofileimage = UserProfileImage.objects.get(user=request.user)
        form = UserProfileForm(request.POST,request.FILES,instance=user_profile)
        userform = UserForm(request.POST, instance=request.user)
        
        if form.is_valid() and userform.is_valid():
            form.save()
            userform.save()
            response_data = {
                'first_name':user_profile.first_name,
                'last_name':user_profile.last_name,
                # 'profile_pic':userprofileimage.profile_pic.url,
            }
            return JsonResponse(response_data)
        else:
            print('form is not valid')
            print(form.errors)
            print(userform.errors)
    userform = UserForm(instance=request.user)
    user_profile = UserProfileImage.objects.get(user=request.user)   
    userprofileform = UserProfileForm(instance=user_profile)
    
    context = {
        'userprofileform':userprofileform,
        'user_profile':user_profile,
        'userform':userform,
    }
    return render(request,'accounts/edit_profile.html',context)



def my_orders(request) :
    orders = Order.objects.filter(user=request.user).order_by('-updated_at')
    paginator = Paginator(orders,10)
    print('paginator:',paginator)
    page = request.GET.get('page')
    print('page:',page)
    paged_orders = paginator.get_page(page)
    print('paged_orders:',paged_orders) 
    return render(request,'accounts/my_orders.html',{'paged_orders':paged_orders})

def user_order_details(request,id) :
    
    order = Order.objects.get(id=id)

    print("jkhfdkjla<HKD")
    print(order)
    order_products = OrderProduct.objects.filter(order_id=id)
    print(order_products)
    context= {
        'order' : order , 
        'order_products' : order_products ,
    }
    return render(request,'accounts/user_order_details.html',context)

@login_required(login_url = 'user_login')
def my_address(request):
    
    
    if request.method == "POST":

        address_id = request.POST['addr_id']
        if address_id == '':
            form = AddressForm(request.POST)
            if form.is_valid():
                address = form.save(commit=False)
                address.user = request.user
                address.save()
                return JsonResponse({'title':'Success', 'text':'Address Updated','icon':'success'})
            else:
                return JsonResponse({'title':'Error', 'text':'Please fill the enter valid address','icon':'warning'})

        else:
            
            address = Address.objects.get(id=address_id)
            
            form = AddressForm(request.POST,instance=address)
            if form.is_valid():
                form.save()
                return JsonResponse({'title':'Success', 'text':'Address Updated','icon':'success'})
            else:
                return JsonResponse({'title':'Error', 'text':'Please fill the enter valid address','icon':'warning'})

    addresses = Address.objects.all().filter(user=request.user)
    form = AddressForm()
    context = {
        'form':form,
        'addresses':addresses,
    }
    return render(request,'accounts/my_address.html',context)

@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.save()
            address.user.add(request.user)
            
            return redirect('checkout')  
    else:
        form = AddressForm()
    
    # Retrieve all addresses associated with the current user
    user_addresses = Address.objects.filter(user=request.user)

    return render(request, 'accounts/add_address.html', {'form': form, 'user_addresses': user_addresses}) 
    
@login_required(login_url='user_login')
def del_addr(request,address_id):
    
    try:
        address = Address.objects.get(id=address_id)
        address.delete()
        return JsonResponse({'msg':'Deleted successfully'})
    except Address.DoesNotExist:
        pass



def invoice(request, order_item_id):
    print('orderitem id : ', order_item_id)
    ordered_product = OrderProduct.objects.get(id=order_item_id, order__user=request.user)
    print("ordered_product:",ordered_product)
    context = {
        'item':ordered_product,
        'discount':0,
    }
    return render(request,'accounts/invoice.html',context)




class generateInvoice(View):

    def get(self, request, orderitem_id, *args, **kwargs):
        try:
            orderproduct = OrderProduct.objects.get(id=orderitem_id)
        except:
            return HttpResponse('505 not found')
        context = {
            'item':orderproduct,
            'discount':0,
        }
        
        pdf = render_to_pdf('accounts/printinvoice.html',context)
        return HttpResponse(pdf, content_type='application/pdf')
    
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

