from django.urls import path,include
from . import views


urlpatterns = [
        path('category/',views.my_admin_category , name = 'my_admin_category'),
        path('category-add/',views.catagory_add , name = 'category-add'),
        path('Catagory/delete_category/<int:id>/',views.delete_category , name = 'delete_category'),
        path('update_catagory/<int:id>/',views.update_catagory , name = 'update_catagory'),
        
     ] 