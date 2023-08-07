from django.urls import path
from . import views


urlpatterns = [

    path('',views.my_admin_view , name = 'my_admin_view'),
    path('users-list',views.users_list,name = 'users-list'),
    path('product-list/',views.product_listt,name='product_listt'),
    # path('block_user/<int:id>/',views.block_user,name='block_user'),
    path('add_product/',views.add_product,name='add_product'),
    path('update_product/<int:id>',views.update_product,name='update_product'),
    path('delete_product/<int:id>',views.delete_product, name="delete_product"),
    path('block_user/<int:id>/',views.block_user,name='block_user'),
    path('change_status/<int:orderproduct_id>/<str:new_status>/', views.change_status, name='change_status'),
    path('sales_report', views.sales_report, name='sales_report'),
    path('monthly_sales', views.monthly_sales, name='monthly_sales'),
    
]
    

    
