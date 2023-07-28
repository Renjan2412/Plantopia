from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
import razorpay
from carts.models import Address, CartItem
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
        amount=request.POST.get('grandPriceText')
        print(amount)
        grand_total = amount

        
        
        if payment_method == "Razor Pay":
            client = razorpay.Client(auth=(settings.KEY, settings.SECRET))

            amount=request.POST.get('grandPriceText')
            print('type of amount : ', type(amount))
            grand_total = round(float(amount))
            

# Print the datatype
            print(amount)
            razor_payment = client.order.create({ "amount": grand_total*100, "currency": "INR", "receipt": "order_rcptid_11" })

            print(razor_payment)
            print(razor_payment['id'])
            print("abhilash")
            cart_items = CartItem.objects.filter(user=request.user)
            address_id = request.POST.get('addressID') 
            print("abhilash1")  
            # address_details = Address.objects.get(id=address)
            address = get_object_or_404(Address, pk= address_id)
            print("address_id :", address_id)
            print("abhilash3")

            payment = Payment.objects.create(
                user=request.user,
                payment_method=request.POST.get('paymentmethod'),
                amount_paid=request.POST.get('grandPriceText'),
            )
            payment.save()

            print("abhilash4")


            order = Order.objects.create(
                user=request.user,
                payment=payment,
                address=address,
                order_total=grand_total,
                status="New",
                GST="6"
            )
            order.save()
            print('abhilash5')

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
                print('abhilash6')



                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()
                print('abhilash7')
                
            response_data = {'order_id': ordered_product.id,
                             'payment_id': razor_payment['id'],
                             'amount_paid': razor_payment['amount'],
                             'key': settings.KEY,
                             'orders_id':order.id
                             }
            print('abhilash8')
          
            return JsonResponse({'response': response_data})
        
        else:
            print('cash on delivery')
            print('request.post : ', request.POST)
            cart_items = CartItem.objects.filter(user=request.user)
            address_id = request.POST.get('addressID')
            address = get_object_or_404(Address, pk= address_id)
            amount_paid =request.POST.get('grandPriceText'),
            print('amount : ', amount_paid)

            payment = Payment.objects.create(
                user=request.user,
                payment_method=request.POST.get('paymentmethod'),
                amount_paid=grand_total,
            )
            payment.save()
            print('payment successful')

            order = Order.objects.create(
                user=request.user,
                payment=payment,
                address=address,
                order_total=grand_total,
                status="New",
                GST="6"
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





def order_success(request):
    order_id = request.GET.get('order_id')
  
    orders_id = request.GET.get('orders')
    print(orders_id)
    ordered_products = OrderProduct.objects.filter(order_id=orders_id)  
    order = Order.objects.get(id=order_id)           
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
    address = order.address
    ordered = order.is_orderd
    is_paid = OrderProduct.is_paid
    status = order.status
    quantity = OrderProduct.quantity
    payment = order.payment      
    context = {
        'order' : order,
        'order_id': order_id,
        'quantity': quantity,
        'product_price':selling_price,
        'product_name': product_dict['product_name'],
        'ordered':ordered,
        'is_paid':is_paid,
        'user': str(user),
        'address':address,
        'status':status,
        'product':product,
        'payment':payment,
        'image_url':product_image,
        'ordered_products': ordered_products,
    }                                    
    return render(request,'orders/order_success.html',context)       


    
