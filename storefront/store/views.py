from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from .models import Product, Customer, Address, Collection, Cart, CartItem, OrderItem, Review, Order
from .serializer import ProductSerializer, CollectionSerializer, ReviewSerializer, CartSerializer, CartItemSerializer
from .serializer import AddCartItemSerializer, UpdateCartItemSerializer, CustomerSerializer, OrderSerializer,\
    OrderCreateSerializer, UpdateOrderSerializer
from django.db.models import Count
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from .pagination import DefaultPagination
from .permissions import IsAdminorReadOnly
from rest_framework.permissions import IsAdminUser, IsAuthenticated


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    permission_classes = [IsAdminorReadOnly]
    search_fields = ['title','description']
    ordering_fields = ['unit_price','last_update']

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):  # a delete method implemented
        if OrderItem.objects.filter(product_id=kwargs['pk']):
            return Response({'Error': 'Product with associated order items cannot be '
                                      'deleted '}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.delete()


class CollectionViewSet(ModelViewSet):
    serializer_class = CollectionSerializer
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    permission_classes = [IsAdminorReadOnly]

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.products.count() > 0:
            return Response({'Error':'Collection with associated products can\'t be deleted'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# handles every query pertaining to review
class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = [IsAdminorReadOnly]

    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}    # the self.kwargs contain the url query parameters


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.prefetch_related('cart_items__product').all()

class CartItemViewSet(ModelViewSet):
    # define method allowed for this veiw set
    http_method_names = ['get','post','patch','delete']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CartItemSerializer
        elif self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer

    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).\
                select_related('product').all()

class CustomerViewSet(ModelViewSet):
    # the delete view set is not supported for this class since we can actually delete a customer by deleting the user
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    permission_classes = [IsAdminUser]

    # to get the customer profile -- customer/me endpoint
    @action(detail=False, methods=['GET','PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        (customer, created) = Customer.objects.get_or_create(user_id=request.user.id)
        # the tuple unpacking is used since the get_or_create manager method returns a tuple of (user, created(boolean)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        if request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    http_method_names = ['get','post','patch','head','delete','head']

    def get_permissions(self):
        if self.request.method in ['PATCH','DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


    def create(self, request, *args, **kwargs):
        """ create an order using just the cart id and return the serialized order object created"""
        serializer = OrderCreateSerializer(data=request.data, context={'user_id':self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        # return the order for the authenticated customer
        (customer_id, created) = Customer.objects.only('id').get(user_id=user.id)
        order = Order.objects.filter(customer_id=customer_id)
        return order