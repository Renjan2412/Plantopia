from django.db import models
from accounts.models import Account
from carts.models import Address
from store.models import Product

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
        ('Pending' , 'Pending'),
        ('Completed' , 'Completed'),
        ('Cancelled' , 'Cancelled'),
    )   

    user = models.ForeignKey(Account , on_delete=models.SET_NULL , null=True)
    payment = models.ForeignKey(Payment , on_delete=models.SET_NULL , blank=True ,null=True)
    order_number = models.CharField(max_length=20)
    address=models.ForeignKey(Address, on_delete=models.SET_NULL , blank=True ,null=True)
    # first_name = models.CharField(max_length=50)
    # last_name = models.CharField(max_length=50)
    # phone_number = models.CharField(max_length=15)
    # email = models.EmailField(max_length=20)
    # address_line_1 = models.CharField(max_length=100)
    # address_line_2 = models.CharField(max_length=100 , blank=True)
    # country = models.CharField(max_length=50,blank=True)
    # state = models.CharField(max_length=50)
    # city = models.CharField(max_length=50)
    order_note = models.CharField(max_length=200 , blank=True)
    order_total = models.FloatField()
    GST = models.FloatField()
    status = models.CharField(max_length=10 , choices=STATUS , default='New')
    ip = models.CharField(blank=True , max_length=20)
    is_orderd = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        ordering = ["-is_orderd"]

    def __str__(self):
        return f"Order {self.id} by {self.user}"

    # def full_name(self) :
    #     return f'{self.first_name} {self.last_name}'
    
    # def full_address(self) :
    #     return f'{self.address_line_1} , {self.address_line_2}'
    
    # def __str__(self) :
    #     return self.first_name
    
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

    def __str__(self) :
         return self.product.product_name

    # order = models.ForeignKey(Order,on_delete=models.CASCADE)
    # product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_products")
    # address = models.ForeignKey(Address,on_delete=models.CASCADE,default=0)
    # quantity = models.IntegerField()
    # product_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # ordered = models.BooleanField(default=False)
    # is_paid = models.BooleanField(default=False)
    # status = models.CharField(max_length=255, default="pending")
    # payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="order_products" )
    # user = models.ForeignKey(CustomUser , on_delete=models.CASCADE, related_name="order_products")

    # def __str__(self):
    #     return f"{self.product} - {self.quantity}"
        

