from django.urls import path
from . import views

urlpatterns = [
        path('' ,views.store , name='store'),
        path('category/<slug:catagory_slug>/',views.store , name = 'product-by-catagory'),
        path('category/store/<slug:catagory_slug>/<slug:product_slug>/',views.product_detail , name = 'product_detail'),
        path('search',views.search, name='search'),
        # path('search_suggestions/',views.search_suggestions, name='search_suggestions'),
        path('wishlist',views.wishlist, name='wishlist'),
        path('add_to_wishlist/',views.add_to_wishlist, name='add_to_wishlist'),
        path('del_wishlist_item/',views.del_wishlist_item, name='del_wishlist_item'),

       
     ] 