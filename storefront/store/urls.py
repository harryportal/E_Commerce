from django.urls import path, include
from . import views
from rest_framework_nested import routers

app_name = 'store'
router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet)


# a base router to be nested with the reviews router
# the look up field is used to look up the primary key in a product_pk format
product_router = routers.NestedSimpleRouter(router, 'products', lookup='product')
product_router.register('reviews', views.ReviewViewSet, basename='products-review')

cart_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = [
    path('', include(router.urls)),
    path('',include(product_router.urls)),
    path('', include(cart_router.urls))
]