from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from .forms import RegistrationForm,UserForm,UserProfileForm
from .models import Account , UserProfile
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
from carts.models import Cart,CartItem
import requests,logging
from urllib.parse import urlparse, parse_qs

# Create your views here.

# def home(request) :
    
#     products = Product.objects.all().filter(is_available=True)

#     context = {
#         'products' : products,
#     }
#     return render(request,'home.html',context)
def home(request):
    sort_option = request.GET.get('sort_option', 'default')

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

    context = {
        'products': products,
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
      
           
            return redirect('user_login')
        
    return render(request,'accounts/user_login.html')

def login_otp(request) :
     if request.user.is_authenticated:
        return redirect('home')
     if request.method == 'POST':
        phone_number = request.POST['phone_number']
        # if not re.match(r'^[0-9]+$',phone_number):
        #     messages.error(request,'Phone number should contain only digits')
        # if len(phone_number)<10:
        #     messages.error(request,'Please provide a valid Phone number')
        if Account.objects.all().filter(phone_number=phone_number):
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
    return render(request , 'accounts/dashboard.html')

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
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None
    if request.method == "POST" :
        user_form = UserForm(request.POST,instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if user_form.is_valid() and profile_form.is_valid() :
            user_form.save()
            profile_form.save()
            messages.success(request,'Your Profile Has Been Updated')
            return redirect('edit_profile')
    else :
        user = request.user
        userprofile = get_object_or_404(UserProfile, user=user)
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'userprofile' : userprofile,
        'user_form' : user_form,
        'profile_form' : profile_form,
    }    

    return render(request,'accounts/edit_profile.html',context)
