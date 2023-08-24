from django.db import models
from accounts.models import Account
from carts.models import Address
from store.models import Product
from django.utils import timezone
import datetime
from offer.models import Coupon

# Create your models here.

class Payment(models.Model) :
    PAYMENT_METHOD_CHOICES = (
        ("cash", "Cash"),
        ("Razorpay", "Razorpay"),
    )
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payment_method} - {self.amount_paid}"
    

class Order(models.Model) :
    STATUS = (
        ('Delivered' , 'Delivered'),
        ('Shipped' , 'Shipped'),
        ('Order Placed' , 'Order Placed'),
        ('Out for Delivery' , 'Out for Delivery'),
        ('Cancelled' , 'Cancelled'),
    )   

    user = models.ForeignKey(Account , on_delete=models.SET_NULL , null=True)
    payment = models.ForeignKey(Payment , on_delete=models.SET_NULL , blank=True ,null=True)
    coupon = models.ForeignKey(Coupon,on_delete=models.CASCADE,blank=True, null=True)
    address=models.ForeignKey(Address, on_delete=models.SET_NULL , blank=True ,null=True)
    order_number = models.CharField(max_length=20)  
    order_note = models.CharField(max_length=200 , blank=True)
    order_total = models.FloatField()
    GST = models.FloatField()
    sub_total = models.FloatField(null=True)
    status = models.CharField(max_length=20 , choices=STATUS , default='New')
    ip = models.CharField(blank=True , max_length=20)
    is_orderd = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
     

    class Meta:
        ordering = ["-is_orderd"]

    def __str__(self):
        return f"Order {self.id} by {self.user}"
    
    def discount_amount(self):
        if self.coupon == None:
            return 0
        else:
            return self.coupon.discount_amount
        
    def order_total_amount(self):
        if self.coupon == None:
            return self.order_total
        else:
            return self.order_total + self.coupon.discount_amount
    

    
class OrderProduct(models.Model) :
    order = models.ForeignKey(Order , on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment , on_delete=models.SET_NULL , blank=True , null=True)
    user = models.ForeignKey(Account , on_delete=models.CASCADE)
    product = models.ForeignKey(Product , on_delete=models.CASCADE)
    address = models.ForeignKey(Address,on_delete=models.CASCADE) 
    quantity = models.IntegerField()
    product_price = models.FloatField()
    orderd = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=255, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # print('save is workinggg....')
        if self.status == 'Shipped':
            self.shipped_date = datetime.datetime.now(tz=timezone.utc)
        if self.status == 'Out For Delivery':
            self.out_for_delivery_date = datetime.datetime.now(tz=timezone.utc)
        if self.status == 'Delivered':
            self.delivered_date = datetime.datetime.now(tz=timezone.utc)
        if self.status == 'Cancelled':
            self.cancelled_date = datetime.datetime.now(tz=timezone.utc)
        if self.status == 'Returned':
            self.returned_date = datetime.datetime.now(tz=timezone.utc)
        super(OrderProduct, self).save(*args, **kwargs)

    def __str__(self) :
         return self.product.product_name
    
    def total(self):
        return self.product_price * self.quantity

   

