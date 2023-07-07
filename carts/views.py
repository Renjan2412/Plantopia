from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product
from carts.models import Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

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
    cart_item = CartItem.objects.get(product=product,cart=cart)
    if cart_item.quantity > 1 :
        cart_item.quantity -= 1
        cart_item.save()
    else :
        cart_item.delete()
    return redirect('cart')   

def remove_cart_item(request,product_id) :
    cart = Cart.objects.get(cart_id =_cart_id(request))
    product = get_object_or_404(Product,id =product_id)
    cart_item = CartItem.objects.get(product=product,cart=cart)
    cart_item.delete()
    return redirect('cart')  


def cart(request) :
    total = 0
    quantity=0
    cart_items=None
    GST = 0
    grand_total = 0
    try :
        
        if request.user.is_authenticated :
            
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            print("User is authenticated")
        else :   
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            print("User is not authenticated")
        for cart_item in cart_items :
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity 
        GST = (5 * total)/100
        grand_total = total + GST
    except ObjectDoesNotExist :
        pass        
  
    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'GST'  : GST,
        'grand_total' : grand_total,
    }
    return render(request , 'store/cart.html',context)

@login_required(login_url = 'user_login')
def checkout(request, total = 0,quantity=0,cart_items=None) :
     GST = 0
     grand_total = 0
     try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for item in cart_items :
            if item.product is not None:
                if hasattr(item.product, 'price') and item.product.price is not None:
                    total += (item.product.price * item.quantity)
                    quantity += item.quantity
                else:
                    # Handle case when product price is None
                    pass
            else:
                # Handle case when product is None
                pass
                 
        GST = (5 * total)/100
        grand_total = total + GST    
     except ObjectDoesNotExist :
        pass
     context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'GST'  : GST,
        'grand_total' : grand_total,
    }
     return render(request,'store/checkout.html',context)
