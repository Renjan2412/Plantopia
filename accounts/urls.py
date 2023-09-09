from django.urls import path
from . import views

urlpatterns = [
    path('',views.home ,name='home'),
    path('register',views.register ,name='register'),
    path('user_login/',views.user_login ,name='user_login'),
    path('logout/',views.logout ,name='logout'),
    path('login_otp/',views.login_otp,name='login_otp'),
    path('login_otp_verify/<str:phone_number>/',views.login_otp_verify,name='login_otp_verify'),
    path('dashboard/',views.dashboard ,name='dashboard'),
    path('forgotPassword', views.forgotPassword, name='forgotPassword'),
    path('resetPassword_validate/<uidb64>/<token>/', views.resetPassword_validate, name='resetPassword_validate'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('my_orders/',views.my_orders,name='my_orders'),
    path('user_order_details/<int:id>',views.user_order_details,name='user_order_details'),
    path('invoice/<int:order_item_id>/',views.invoice, name='invoice'),
    path('generateinvoice/<int:orderitem_id>/', views.generateInvoice.as_view(), name='generateinvoice'),
    path('my_address/',views.my_address,name='my_address'),
    path('delete-address/<int:address_id>/',views.del_addr,name='del_addr'),
    path('add_address/',views.add_address,name='add_address'),
    
]
