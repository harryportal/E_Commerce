from django.urls import path
from . import views


app_name = 'store'
urlpatterns = [
    path('products', views.ProductList.as_view(), name='product'),
    path('collections',views.CollectionList.as_view(), name='collections'),
    path('products/<int:pk>', views.ProductDetail.as_view())

]