from django.db import models
from store.models import Product
from accounts.models import Account
from django.contrib.auth import get_user_model


# Create your models here.
class Cart(models.Model) :
    user = models.ForeignKey(Account, on_delete=models.CASCADE,null=True)
    cart_id = models.CharField(max_length=250 , blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self) :
        return self.cart_id

class CartItem(models.Model) :
    user = models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Product , on_delete=models.CASCADE)
    cart    = models.ForeignKey(Cart ,on_delete=models.CASCADE,default=None )
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self) :
        return self.product.price * self.quantity


    def __str__(self) :
        return self.product.product_name
    

User = get_user_model()

class Address(models.Model):
    user = models.ManyToManyField(User)
    first_name = models.CharField(max_length=50,default='')
    last_name = models.CharField(max_length=50,default='')
    address_line_1 = models.CharField(blank=True, max_length=100)
    address_line_2 = models.CharField(blank=True, max_length=100)
    email = models.EmailField(max_length=20,blank=True,null=True)
    city = models.CharField(blank=True, max_length=50)
    state = models.CharField(blank=True, max_length=50)
    country = models.CharField(blank=True, max_length=50)
    phone_number = models.CharField(max_length=20,blank=True,null=True)
    post_code = models.CharField(max_length=15,blank=True)
    order_note = models.CharField(max_length=200 , blank=True,null=True)


    def _str_(self):
        return f"{self.first_name} {self.last_name}" 
    
    # def full_name(self) :
    #     return f'{self.first_name} {self.last_name}'
    
    # def full_address(self) :
    #     return f'{self.address_line_1} , {self.address_line_2}'   

    