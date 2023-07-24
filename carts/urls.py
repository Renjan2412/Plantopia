from django.urls import path
from . import views
from carts.views import CheckoutView

urlpatterns = [
    path('',views.cart,name='cart'),
    path('update_cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('add_cart/<int:product_id>/',views.add_cart,name='add_cart'),
    path('remove_cart/<int:product_id>/',views.remove_cart,name='remove_cart'),
    path('remove_cart_item/<int:product_id>/',views.remove_cart_item,name='remove_cart_item'),
    # path('checkout/',views.checkout,name='checkout'),
    path('checkout',views.CheckoutView.as_view(),name='checkout'),
    path('add_address/',views.add_address,name='add_address'),
]
