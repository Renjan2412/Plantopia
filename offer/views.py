from django.shortcuts import render
from django.http import JsonResponse
from carts.models import CartItem
from .models import Coupon
from datetime import datetime

# Create your views here.
def coupon_verify(request):
    code = request.POST.get('Coupon')
    cart_items = CartItem.objects.filter(user=request.user)
    now = datetime.now()

    total_amount = sum(cart_item.sub_total() for cart_item in cart_items)

    try:
        coupon = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        coupon = None

    if coupon is None:
        return JsonResponse({'message': "Coupon doesn't exist"})

    if total_amount < coupon.min_amount:
        lack_amount = coupon.min_amount - total_amount
        return JsonResponse({'message': f'Please Purchase ₹{lack_amount:.2f} to apply this coupon'})

    if now.date() < coupon.valid_from.date() or now.date() > coupon.valid_to.date():
        return JsonResponse({'message': 'Coupon Expired'})

    new_total = total_amount - coupon.discount_amount
    GST = (5 * new_total) / 100
    final_amount = new_total + GST
    discount_amount = coupon.discount_amount

    return JsonResponse({
        'total_amount': total_amount,
        'discount_amount_foreach': discount_amount,
        'new_total_amount': new_total,
        'coupon_discount': coupon.discount_amount,
        'coupon_id': coupon.id,
        'gst_amount': GST,
        'final_amount': final_amount,
        'message': 'Coupon has been Applied'
    })

# def coupon_verify(request) :
    
#     code = request.POST.get('Coupon')
#     print('code:',code)
#     cart_items = CartItem.objects.filter(user=request.user)
#     now = datetime.now()
    
#     total_amount = 0
#     try:
#         coupon = Coupon.objects.get(code=code)
#         print('coupon:',coupon)
    
#     except:
#         coupon = None
    
#     for cart_item in cart_items:
#         total_amount += cart_item.sub_total()
#         print('total:',total_amount)


#     if(coupon == None):
#         return JsonResponse({'message':"Coupon doesn't exist "})
#     else:
#         if total_amount < coupon.min_amount:
#             lack_amount = coupon.min_amount - total_amount
#             return JsonResponse({'message':'Please Purchase ₹'+ str(lack_amount) + ' to apply this coupon'})
        
#         elif now.date() < coupon.valid_from.date() or now.date() > coupon.valid_to.date():
#             return JsonResponse({'message':'Coupon Expired'})
        
#         else:
#             new_total = total_amount - coupon.discount_amount
#             GST = (5 * new_total) / 100
#             final_amount = new_total + GST
#             print('new_total:',new_total)
#             print('final_amount:',final_amount)
#             discount_amount = coupon.discount_amount/cart_items.count()
#             print('discount_amount:',discount_amount)
#             return JsonResponse({'total_amount':total_amount,
#                                   'discount_amount_foreach':discount_amount, 
#                                   'new_total_amount':new_total, 
#                                   'coupon_discount':coupon.discount_amount,
#                                   'coupon_id':coupon.id,
#                                   'gst_amount': GST,
#                                   'final_amount':final_amount, 
#                                   'message':'Coupon has been Applied' })
