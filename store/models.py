from django.db import models
from Catagory.models import Catagory
from django.urls import reverse
from accounts.models import Account

# Create your models here.

class Product(models.Model) :
    product_name = models.CharField(max_length=200 , unique=True)
    slug         = models.SlugField(max_length=200 , unique=True)
    description  = models.TextField(max_length=600 , blank=True)
    price        = models.IntegerField()
    images       = models.ImageField(upload_to='photos/products')
    # hover_images = models.ImageField(upload_to='photos/products')
    stock        = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    catagory     = models.ForeignKey(Catagory, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date= models.DateTimeField(auto_now=True)


    def get_url(self) :
        return reverse('product_detail' , args = [self.catagory.slug , self.slug])

    def __str__(self) :
        return self.product_name

class Picture(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_pictures")
    image = models.ImageField(upload_to='photos/products', blank=True)
    

    def __str__(self):
        return self.image.url
    
class Wishlist(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)

    def __str__(self):
       return f"{self.user} - {self.product.product_name}"    