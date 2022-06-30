from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

app_name = 'store'
router = DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('collections', views.CollectionViewSet)


urlpatterns = [
    path('', include(router.urls)),
]