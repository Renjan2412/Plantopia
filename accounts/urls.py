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
    path('edit_profile/',views.edit_profile,name='edit_profile'),
]
