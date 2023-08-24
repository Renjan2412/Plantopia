
from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from django.views import View
from store.models import Product
from carts.models import Cart,CartItem,Address
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from accounts.models import Account
from accounts.forms import UserProfileForm
from django.http import JsonResponse
from .forms import AddressForm
from offer.models import Coupon
from offer.forms import CouponForm
from django.utils import timezone

# Create your views here.
def _cart_id(request) :
    cart = request.session.session_key
    if not cart :
        cart = request.session.create()
    return cart    

@login_required(login_url='user_login')
def add_cart(request , product_id) :
    product = Product.objects.get(id=product_id)  # to get the product
    # Get or create a cart for the user
    cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))
    if created:
        cart.save()

    # Associate the user with the cart
    cart.user = request.user
    cart.save()
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
    coupon_form = CouponForm(request.POST or None)
    context = {}

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

        

        if request.method == 'POST' and coupon_form.is_valid() :
            coupon_code = coupon_form.cleaned_data['coupon_code']
            try :
                coupon = Coupon.objects.get(code=coupon_code, active=True)
                if coupon.valid_from <= timezone.now() <= coupon.valid_to :
                    discount_percentage = coupon.discount_amount
                    discount = (discount_percentage / 100) * total
                    grand_total -= discount
                    context['applied_coupon'] = coupon
            except Coupon.DoesNotExist :
                context['coupon_error'] = 'Invalid coupon code..'

        GST = (5 * total) / 100
        grand_total = total + GST
        print('total:' ,total)
        print('GST:' ,GST)
        print('grand_total:' ,grand_total)

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'GST': GST,
        'grand_total': grand_total,
        'coupon_form' : coupon_form,
    }
    if request.method == 'POST' and coupon_form.is_valid():
         return redirect('cart')
    return render(request, 'store/cart.html', context)



# def update_cart(request, product_id):
#     if request.method == "POST" and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
#         quantity = int(request.POST.get("quantity", 1))

#         try:
#             cart_item = CartItem.objects.get(product_id=product_id, user=request.user, is_active=True)
#             cart_item.quantity = quantity
#             cart_item.sub_total = cart_item.product.price * quantity
#             cart_item.save()

#             # Recalculate the total, GST, and grand_total based on updated cart items
#             cart_items = CartItem.objects.filter(user=request.user, is_active=True)
#             total = sum(item.product.price * item.quantity for item in cart_items)
#             GST = (5 * total) / 100
#             grand_total = total + GST

#             # Check if a coupon is applied and adjust calculations accordingly
#             # coupon_discount = 0
#             # if cart_item.coupon_applied:
#             #     print("coupon applied on cart")
#             #     coupon_discount = cart_item.coupon.discount_amount
#             #     total -= coupon_discount

#             data = {
#                 "success": True,
#                 "sub_total": cart_item.sub_total,
#                 "total": total,
#                 "GST": GST,
#                 "grand_total": grand_total,
#                 # "coupon_applied": cart_item.coupon_applied,
#                 # "coupon_discount": coupon_discount,
#                 "new_total_amount": total  # Adjust if needed based on coupon logic
#             }
            
#             return JsonResponse(data)
#         except CartItem.DoesNotExist:
#             data = {"success": False, "message": "Cart item not found."}
#             return JsonResponse(data, status=400)
#     else:
#         data = {"success": False, "message": "Invalid request."}
#         return JsonResponse(data, status=400)



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
            print('type:' ,type(total))
            print('type:' ,type(GST))
            print('type:' ,type(grand_total))

            data = {
                "success": True,
                "sub_total": cart_item.sub_total,
                "total": total,
                "GST": GST,
                "grand_total": grand_total
            }
            print('data: ',data)
            
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
    # @login_required
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

            coupon_id = request.GET.get('coupon_id')
            print('coupon_id checkout:',coupon_id)
            coupon_discount = 0
            if coupon_id:
                try:
                    coupon = Coupon.objects.get(id=coupon_id)
                    grand_total -= coupon.discount_amount
                    coupon_discount = coupon.discount_amount
                except Coupon.DoesNotExist:
                    pass
            
            
            print('coupon_discount:',coupon_discount)
            context = {
                
                'cart_items': cart_items,
                'address': address,
                'total_total': subtotal,
                'cart': cart.cart_id,
                'GST':GST,
                'coupon_discount':coupon_discount,
                'grand_total':grand_total,
            }
            print("####",context)

            # storing GST into session 

            # request.session['order_GST'] = GST
            # request.session['total_total'] = subtotal

            return render(request, 'store/checkout.html', context)
        except Cart.DoesNotExist:
            pass
            return HttpResponse("Cart does not exist.")

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