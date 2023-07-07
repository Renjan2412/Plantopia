from django.contrib import admin
from store.models import Product,Picture
from Catagory.models import Catagory


# class MyAdminView(admin.AdminSite) :
#     site_header = 'Plantopia Admin'
#     site_title = 'Plantopia'

# plantopia_admin = MyAdminView(name='Admin')

# # Register your models here.

# plantopia_admin.register(admin)



admin.site.register(Picture)


# @admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price')
    fields = ('product_name', 'description', 'price')