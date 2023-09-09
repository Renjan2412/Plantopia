from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
import razorpay
from carts.models import Address, CartItem,Cart
# from .forms import OrderForm
from .models import Order,Payment,OrderProduct
import datetime,uuid
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.conf import settings
from accounts.models import Wallet
from django.contrib.auth.decorators import login_required
from offer.models import Coupon
# Create your views here.

def payments(request) :
    return render(request, 'orders/payments.html')
    
#ajax method to create order
def order(request):
    
    if request.method == 'POST':
        print('hiiiiiiiiiiii')
        print('request.post : ',request.POST)
        coupon_discount = 0
        payment_method = request.POST.get('paymentmethod')
        coupon_id = request.POST.get('coupon_id')
        print('coupon_id:',coupon_id)

        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id)
                coupon_discount = coupon.discount_amount
            except Coupon.DoesNotExist:
                coupon_discount = 0
        else:
            coupon_discount = 0

        print('coupon_discount:',coupon_discount)    
        

        
        if payment_method == "Razor Pay":
            client = razorpay.Client(auth=(settings.KEY, settings.SECRET))

            sub_total = request.POST.get('subTotal')
            print('sub :',sub_total)
            subTotal = float(sub_total)
            amount=request.POST.get('grandPriceText')
            print('type of amount : ', type(amount))
            print(amount)
            grand_total = float(amount)
            grand_total -= coupon_discount

            

# Print the datatype
            print(amount)
            razor_payment = client.order.create({ "amount": grand_total*100, "currency": "INR", "receipt": "order_rcptid_11" })

            print(razor_payment)
            print(razor_payment['id'])
            
            cart_items = CartItem.objects.filter(user=request.user)
            address_id = request.POST.get('addressID') 

            # GST = request.session.get('order_GST' , 0)
            GST = request.POST.get('GST')
            
            # order number generation
            order_number = str(uuid.uuid4())[:8]
              
            # address_details = Address.objects.get(id=address)
            address = get_object_or_404(Address, pk= address_id)
            print("address_id :", address_id)
            

            payment = Payment.objects.create(
                user=request.user,
                payment_method=request.POST.get('paymentmethod'),
                amount_paid=request.POST.get('grandPriceText'),
                status = 'Paid',
            )
            payment.save()

            


            order = Order.objects.create(
                user=request.user,
                payment=payment,
                address=address,
                order_total=grand_total,
                status="Order Placed",
                order_number=order_number,
                GST=GST,
                sub_total=sub_total,
                coupon_id=coupon_id,
                
            )
            order.save()
            

            for cart_item in cart_items:
                ordered_product = OrderProduct.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    product_price=cart_item.product.price,
                    orderd=False,
                    is_paid=False,
                    payment=payment,
                    user=request.user,
                    address=order.address,
                    # GST=order.GST,
                                      
                )
                



                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()
                
                
            response_data = {'order_id': ordered_product.id,
                             'payment_id': razor_payment['id'],
                             'amount_paid': razor_payment['amount'],
                             'key': settings.KEY,
                             'orders_id':order.id,
                             'coupon_id' :coupon_id,
                             
                             }
            
          
            return JsonResponse({'response': response_data})
        
        else:
            print('cash on delivery')
            print('request.post : ', request.POST)
            cart_items = CartItem.objects.filter(user=request.user)
            address_id = request.POST.get('addressID')
            address = get_object_or_404(Address, pk= address_id)
            sub_total = request.POST.get('subTotal')
            print(sub_total)
            subTotal = float(sub_total)
            order_number = str(uuid.uuid4())[:8]
            print(subTotal)
            amount =request.POST.get('grandPriceText')
            print('amount : ', amount)
            grand_total = float(amount)
            grand_total -= coupon_discount
            # GST = request.session.get('order_GST' , 0)
            GST = request.POST.get('GST')

            payment = Payment.objects.create(
                user=request.user,
                payment_method=request.POST.get('paymentmethod'),
                amount_paid=request.POST.get('grandPriceText'),
                status = 'Pending',
            )
            payment.save()
            print('payment successful')

            order = Order.objects.create(
                user=request.user,
                payment=payment,
                address=address,
                order_total=grand_total,
                status="Order_Placed",
                order_number=order_number,
                GST=GST,
                sub_total=subTotal,
                coupon_id=coupon_id,
                
            )
            order.save()
            print('order successful')
            print('address id :' ,address_id)
            print('oreder id :',order)

            for cart_item in cart_items:
                ordered_product = OrderProduct.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    product_price=cart_item.product.price,
                    orderd=False,
                    is_paid=False,
                    payment=payment,
                    user=request.user,
                    address=order.address,
                    
                    
                )

                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()

            response_data = {'order_id': ordered_product.id,
                             'orders_id':order.id,
                             'coupon_id':coupon_id,
                             }
            return JsonResponse({'response': response_data})
    else:
        return JsonResponse({'message': "failed"})



def calculate_total(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.sub_total() for item in cart_items)
    return total




def order_success(request):
    order_id = request.GET.get('order_id')
    orders_id = request.GET.get('orders')
    print(orders_id)
    ordered_products = OrderProduct.objects.filter(order_id=orders_id)  
    print(ordered_products)

    order = OrderProduct.objects.get(id=order_id)           
    print(order)
    product = ordered_products.first().product
    product_dict = model_to_dict(product)    
    # Access the fields from the related Product model
    product_image = product_dict['images'].url
    selling_price = product_dict['price']
    # Retrieve other fields from the OrderProduct model
    user = order.user
    address = order.address
    # ordered = order.is_orderd
    is_paid = OrderProduct.is_paid
    status = order.status
    print('order status:',status)
    quantity = OrderProduct.quantity
    payment = order.order.payment 
    print('payment 1:',payment)
    order_number = order.order.order_number
    cart_items = CartItem.objects.all().filter(user=request.user)
    total=0
    for cart_item in cart_items :
        total += cart_item.sub_total()
    
    GST= order.order.GST
    coupon_discount = order.order.discount_amount
    
    print('coupon_discount :',coupon_discount)
    
    subtotal = order.order.sub_total
    grand_total = order.order.order_total
    print("grand_total : ",grand_total)

    #clear cart
    CartItem.objects.filter(user=request.user).delete()

    context = {
        'order' : order,
        'order_id': order_id,
        'quantity': quantity,
        'product_price':selling_price,
        'product_name': product_dict['product_name'],
        # 'ordered':ordered,
        'is_paid':order.is_paid,
        'user': user,
        'address':address,
        'GST':GST,
        'status':status,
        'product':product,
        'coupon_discount' : coupon_discount,
        'total': total,
        'order_number':order_number,
        'payment':payment,
        'image_url':product_image,
        'ordered_products': ordered_products,
        'subtotal':subtotal,
        'grand_total': grand_total,
        

    }                                    
    return render(request,'orders/order_success.html',context)  

def orderpage(request) :
    orders = Order.objects.all().order_by("-created_at")
    return render(request, "admin-temp/orderpage.html", {"orders": orders})

def order_deatils(request,id) :
    
    order = get_object_or_404(Order, id=id)
    order_items = OrderProduct.objects.filter(order__id=id)
    GST = order.GST
    print('order item:',order_items)
    context = {
        'order_items':order_items,
        'order':order,
        'GST' : GST,
    }

    return render(request,'admin-temp/order_details.html',context)

def edit_order(request, id):
    if request.method == "POST":
        status = request.POST.get("status")
        try:
        
            order = Order.objects.get(pk=id)
            order.status = status
            order.save()
            if status == 'Delivered':
                pyment=order.payment
                pyment.status='Success'
                pyment.save()


        except Order.DoesNotExist:
            pass
    return redirect("orderpage")


def cancel_product(request):
    if request.method == 'POST':
        order_product_id = request.POST.get('orderproduct_id')
        
        try:
            order_product = OrderProduct.objects.get(id=order_product_id)
            if order_product.status != 'Cancelled':
                order_product.status = 'Cancelled'
                order_product.save()
                response = {'success': True, 'message': 'Product has been cancelled.'}
            else:
                response = {'success': False, 'message': 'Product is already cancelled.'}
        except OrderProduct.DoesNotExist:
            response = {'success': False, 'message': 'Product not found.'}
        
        return JsonResponse(response)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})
         

@login_required(login_url='user_login')
def order_act(request):
    
    orderproduct_id = request.POST.get('orderproduct_id')
    print("orderproduct_id :",orderproduct_id)
    orderproduct = OrderProduct.objects.get(order__user=request.user,id=orderproduct_id)
    product = orderproduct.product
    print("product :",product)
    order = orderproduct.order
    order.order_total -= orderproduct.total()
    orderproduct.status = 'Cancelled'
    payment_method = orderproduct.order.payment.payment_method
    if payment_method != 'Cash On Delivery':
        wallet = Wallet.objects.filter(user_id=orderproduct.order.user.id)
        Wallet.balance += orderproduct.order.order_total
        wallet.save()
    # orderproduct.product_price = 0
    product.stock += orderproduct.quantity
    
    product.save()
    orderproduct.save()
    order.save()
    return JsonResponse({'message':'hi'}) 

@login_required(login_url='user_login')
def order_return(request):
    orderproduct_id = request.POST.get('orderproduct_id')
    orderproduct = OrderProduct.objects.get(order__user=request.user, id=orderproduct_id)
    orderproduct.status = 'Return Requested'
    orderproduct.save()
    return JsonResponse({'message':'The return for the product has been requested...'})   
