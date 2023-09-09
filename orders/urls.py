from django.urls import path
from . import views

urlpatterns = [
   # path('place_order',views.place_order,name='place_order'),
   path('payments',views.payments,name='payments'),
   path('order/',views.order,name='order'),
   path('order_success',views.order_success,name='order_success'),
   path('orderpage/',views.orderpage,name='orderpage'),
   path('order_details/<int:id>/',views.order_deatils,name='order_details'),
   # path('cancel-product/', views.cancel_product, name='cancel_product'),
   path('edit_order/<int:id>/',views.edit_order,name='edit_order'),
   path('cancel_order/<int:id>/', views.cancel_product, name='cancel_order'),
   path('order-act/', views.order_act, name='order_act'),
   path('order-return/', views.order_return, name='order_return'),

   ] 