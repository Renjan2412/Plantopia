from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
import razorpay
from carts.models import Address, CartItem,Cart
# from .forms import OrderForm
from .models import Order,Payment,OrderProduct
import datetime
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.conf import settings

# Create your views here.

def payments(request) :
    return render(request, 'orders/payments.html')

# def place_order(request, total=0, quantity=0):
#     current_user = request.user

#     cart_items = CartItem.objects.filter(user=current_user)
#     cart_count = cart_items.count()

#     if cart_count <= 0:
#         return redirect('store')

#     grand_total = 0
#     GST = 0
#     for cart_item in cart_items:
#         total += (cart_item.product.price * cart_item.quantity)
#         quantity += cart_item.quantity

#     GST = (5 * total) / 100
#     grand_total = total + GST

#     if request.method == 'POST':
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             order = form.save(commit=False)  # Create Order instance from form data
#             order.user = current_user
#             order.order_total = grand_total
#             order.GST = GST
#             order.ip = request.META.get('REMOTE_ADDR')
#             order.save()

#             # Generate order number
#             yr = int(datetime.date.today().strftime('%Y'))
#             dt = int(datetime.date.today().strftime('%d'))
#             mt = int(datetime.date.today().strftime('%m'))

#             d = datetime.date(yr, mt, dt)
#             current_date = d.strftime('%Y%mt%d')
#             order_number = current_date + str(order.id)
#             order.order_number = order_number
#             order.save()

#             order = Order.objects.get(user=current_user, is_orderd=False, order_number=order_number)
#             context = {
#                 'order' : order,
#                 'cart_items' : cart_items,
#                 'total' : total,
#                 'GST' : GST,
#                 'grand_total' : grand_total,
#                 }

#             return render(request, 'orders/payments.html' , context)
#         else:
#             print(form.errors)
#             return HttpResponse('Invalid form data')
#     else:
#         return redirect('checkout')
    


    
#ajax method to create order
def order(request):
    
    if request.method == 'POST':
        print('hiiiiiiiiiiii')
        payment_method = request.POST.get('paymentmethod')
        

        
        if payment_method == "Razor Pay":
            client = razorpay.Client(auth=(settings.KEY, settings.SECRET))

            amount=request.POST.get('grandPriceText')
            print('type of amount : ', type(amount))
            print(amount)
            grand_total = float(amount)

            

# Print the datatype
            print(amount)
            razor_payment = client.order.create({ "amount": grand_total*100, "currency": "INR", "receipt": "order_rcptid_11" })

            print(razor_payment)
            print(razor_payment['id'])
            
            cart_items = CartItem.objects.filter(user=request.user)
            address_id = request.POST.get('addressID') 

            GST = request.session.get('order_GST' , 0)
            
              
            # address_details = Address.objects.get(id=address)
            address = get_object_or_404(Address, pk= address_id)
            print("address_id :", address_id)
            

            payment = Payment.objects.create(
                user=request.user,
                payment_method=request.POST.get('paymentmethod'),
                amount_paid=request.POST.get('grandPriceText'),
            )
            payment.save()

            


            order = Order.objects.create(
                user=request.user,
                payment=payment,
                address=address,
                order_total=grand_total,
                status="Pending",
                GST=GST,
                
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
                             
                             }
            
          
            return JsonResponse({'response': response_data})
        
        else:
            print('cash on delivery')
            print('request.post : ', request.POST)
            cart_items = CartItem.objects.filter(user=request.user)
            address_id = request.POST.get('addressID')
            address = get_object_or_404(Address, pk= address_id)
            amount =request.POST.get('grandPriceText')
            print('amount : ', amount)
            grand_total = float(amount)
            GST = request.session.get('order_GST' , 0)

            payment = Payment.objects.create(
                user=request.user,
                payment_method=request.POST.get('paymentmethod'),
                amount_paid=request.POST.get('grandPriceText'),
            )
            payment.save()
            print('payment successful')

            order = Order.objects.create(
                user=request.user,
                payment=payment,
                address=address,
                order_total=grand_total,
                status="Pending",
                GST=GST,
                
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
                             }
            return JsonResponse({'response': response_data})
    else:
        return JsonResponse({'message': "failed"})



def calculate_total(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.sub_total() for item in cart_items)
    return total




def order_success(request):
    GST = 0
    grand_total = 0
    total = 0
    order_id = request.GET.get('order_id')
  
    orders_id = request.GET.get('orders')
    print(orders_id)
    ordered_products = OrderProduct.objects.filter(order_id=orders_id)  
    print(ordered_products)

    order = OrderProduct.objects.get(id=order_id)           
    # order = get_object_or_404(Orders, id=order_id)
    # order = OrderProduct.objects.get(id=order_id)
    print(order)
    product = ordered_products.first().product
    product_dict = model_to_dict(product)    
    # Access the fields from the related Product model
    product_image = product_dict['images'].url
    selling_price = product_dict['price']
    # Retrieve other fields from the OrderProduct model
    user = order.user
    print(user)
    
    address = order.address
    # ordered = order.is_orderd
    is_paid = OrderProduct.is_paid
    status = order.status
    quantity = OrderProduct.quantity
    payment = order.payment 

    # GST= order.GST

    
    cart = Cart.objects.filter(user=request.user)
    print("3333333333333333333")
    print(cart)
    for item in ordered_products:
        item.total_quantity = item.quantity * item.product_price


    
    subtotal = calculate_total(request)   
    GST = (5 * subtotal)/100
    grand_total = subtotal + GST

    context = {
        'order' : order,
        'order_id': order_id,
        'quantity': quantity,
        'product_price':selling_price,
        'product_name': product_dict['product_name'],
        # 'ordered':ordered,
        'is_paid':is_paid,
        'user': user,
        'address':address,
        'GST':GST,
        'status':status,
        'product':product,
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
    context = {
        'order_items':order_items,
        'order':order,
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


# def cancel_product(request):
#     if request.method == 'POST':
#         order_product_id = request.POST.get('orderproduct_id')
        
#         try:
#             order_product = OrderProduct.objects.get(id=order_product_id)
#             if order_product.status != 'Cancelled':
#                 order_product.status = 'Cancelled'
#                 order_product.save()
#                 response = {'success': True, 'message': 'Product has been cancelled.'}
#             else:
#                 response = {'success': False, 'message': 'Product is already cancelled.'}
#         except OrderProduct.DoesNotExist:
#             response = {'success': False, 'message': 'Product not found.'}
        
#         return JsonResponse(response)
#     else:
#         return JsonResponse({'success': False, 'message': 'Invalid request method.'})
         
def cancel_order(request,id):
    order = Order.objects.get(pk = id)
    order.status="cancelled"
    order.save()
    return redirect('user_order_details')

    
