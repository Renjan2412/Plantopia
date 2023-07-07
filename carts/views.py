
from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from django.views import View
from store.models import Product
from carts.models import Cart,CartItem,Address
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from accounts.models import Account,UserProfile
from accounts.forms import UserProfileForm
from django.http import JsonResponse
from .forms import AddressForm

# Create your views here.
def _cart_id(request) :
    cart = request.session.session_key
    if not cart :
        cart = request.session.create()
    return cart    

@login_required(login_url='user_login')
def add_cart(request , product_id) :
    product = Product.objects.get(id=product_id)  # to get the product
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
    except Cart.DoesNotExist :
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )    
    cart.save()    

    try :
        if request.user.is_authenticated :
            user = request.user
        else :
            user = None    
        cart_item = CartItem.objects.get(product=product , cart=cart , user=user)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist :
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
            user = request.user,
        )  
        cart_item.save()  
    return redirect('cart')    

def remove_cart(request , product_id) :
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product , id = product_id)
    try :
        cart_item = CartItem.objects.get(product=product,cart=cart)
        if cart_item.quantity > 1 :
            cart_item.quantity -= 1
            cart_item.save()
        else :
            cart_item.delete()
    except CartItem.DoesNotExist :
        pass        
    return redirect('cart')   

def remove_cart_item(request,product_id) :
    cart = Cart.objects.get(cart_id =_cart_id(request))
    product = get_object_or_404(Product,id =product_id)
    cart_item = CartItem.objects.get(product=product,cart=cart)
    cart_item.delete()
    return redirect('cart')  


def cart(request):
    total = 0
    quantity = 0
    cart_items = None
    GST = 0
    grand_total = 0

    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            cart_item.sub_total = cart_item.product.price * cart_item.quantity
            total += cart_item.sub_total
            quantity += cart_item.quantity

        GST = (5 * total) / 100
        grand_total = total + GST
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'GST': GST,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)




def update_cart(request, product_id):
    if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        quantity = int(request.POST.get("quantity", 1))

        try:
            cart_item = CartItem.objects.get(product_id=product_id, user=request.user, is_active=True)
            cart_item.quantity = quantity
            cart_item.sub_total = cart_item.product.price * quantity
            cart_item.save()

            # Recalculate the total, GST, and grand_total based on updated cart items
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            total = sum(item.product.price * item.quantity for item in cart_items)
            GST = (5 * total) / 100
            grand_total = total + GST

            data = {
                "success": True,
                "sub_total": cart_item.sub_total,
                "total": total,
                "GST": GST,
                "grand_total": grand_total
            }
            return JsonResponse(data)
        except CartItem.DoesNotExist:
            data = {"success": False, "message": "Cart item not found."}
            return JsonResponse(data, status=400)
    else:
        data = {"success": False, "message": "Invalid request."}
        return JsonResponse(data, status=400)






def calculate_total(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.sub_total() for item in cart_items)
    return total







class CheckoutView(View):
    def get(self, request):
        GST = 0
        grand_total = 0
        try:
            cart = Cart.objects.filter(user=request.user).latest('date_added')
            print("####",cart)
            cart_items = CartItem.objects.filter(user=request.user)
            print("####",cart_items)
            subtotal = calculate_total(request)
            address = Address.objects.filter(user=request.user)
            GST = (5 * subtotal)/100
            grand_total = subtotal + GST
            
            
            context = {
                'cart_items': cart_items,
                'address': address,
                'total_total': subtotal,
                'cart': cart.cart_id,
                'GST':GST,
                'grand_total':grand_total,
            }
            print("####",context)

            return render(request, 'store/checkout.html', context)
        except Cart.DoesNotExist:
            # Handle the case when the Cart object doesn't exist
            # You can redirect the user to a cart creation page or display an error message
            return HttpResponse("Cart does not exist.")

    
    
# def add_address(request):
#         if request.method == 'POST':
#             print('post : ',request.POST)
#             first_name = request.POST.get('first_name')
#             last_name = request.POST.get('last_name')
#             address_line_1 = request.POST.get('address_line_1')
#             address_line_2 = request.POST.get('address_line_2')
#             phone_number = request.POST.get('phone_number')
#             email = request.POST.get('email')
#             city = request.POST.get('city')
#             state= request.POST.get('state')
#             country= request.POST.get('country')
#             order_note = request.POST.get('order_notes')
#             # print(request.body)
#             # print(name, city, pincode, phone,address)

#             address = Address.objects.create(
#                 user=request.user,
#                 first_name=first_name,
#                 last_name=last_name,
#                 address_line_1=address_line_1,
#                 address_line_2=address_line_2,
#                 city=city,
#                 state=state,
#                 phone_number=phone_number,
#                 country=country,
#                 email=email,
#                 order_note=order_note,
#             )
#             address.save()
#             return redirect('checkout')  
        
#         return render(request, 'accounts/add_address.html') 
# 

@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.save()
            address.user.add(request.user)
            
            return redirect('checkout')  # Replace 'checkout' with the appropriate URL name
    else:
        form = AddressForm()
    
    # Retrieve all addresses associated with the current user
    user_addresses = Address.objects.filter(user=request.user)

    return render(request, 'accounts/add_address.html', {'form': form, 'user_addresses': user_addresses})   