from django.db import models
from django.urls import reverse

# Create your models here.
class Catagory(models.Model) :
    catagory_name = models.CharField(max_length=60 , unique = True , null=False)
    slug = models.SlugField(max_length=100 , unique= True)
    description = models.TextField(max_length=350 , blank= True)
    cat_image = models.ImageField(upload_to = 'photos/catagories',blank=True)
    


    class Meta:
        verbose_name = 'Catagory'
        verbose_name_plural = 'Catagories'

    def get_url(self) :
        return reverse('product-by-catagory' , args=[self.slug])

    def __str__(self):
        return self.catagory_name
