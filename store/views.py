from datetime import datetime

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.views import APIView

from core.models import User
from .models import Product, Customer, Address, Collection, Cart, CartItem, OrderItem, Review, Order, ProductImage
from .serializer import ProductSerializer, CollectionSerializer, ReviewSerializer, CartSerializer, CartItemSerializer
from .serializer import AddCartItemSerializer, UpdateCartItemSerializer, CustomerSerializer, OrderSerializer, \
    OrderCreateSerializer, UpdateOrderSerializer, ProductImageSerializer
from django.db.models import Count
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from .pagination import DefaultPagination
from .permissions import IsAdminorReadOnly
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from storefront.settings import prod
import requests
from django.core.mail import send_mail, mail_admins


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related('images').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    permission_classes = [IsAdminorReadOnly]
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']

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
            return Response({'Error': 'Collection with associated products can\'t be deleted'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# handles every query pertaining to review
class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = [IsAdminorReadOnly]

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}  # the self.kwargs contain the url query parameters


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.prefetch_related('cart_items__product').all()


class CartItemViewSet(ModelViewSet):
    # define method allowed for this veiw set
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CartItemSerializer
        elif self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']). \
            select_related('product').all()


class CustomerViewSet(ModelViewSet):
    # the delete view set is not supported for this class since we can actually delete a customer by deleting the user
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    permission_classes = [IsAdminUser]

    # to get the customer profile -- customer/me endpoint
    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
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
    http_method_names = ['get', 'post', 'patch', 'head', 'delete', 'head']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """ create an order using just the cart id and return the serialized order object created"""
        serializer = OrderCreateSerializer(data=request.data, context={'user_id': self.request.user.id})
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
        customer_id = Customer.objects.only('id').get(user_id=user.id)
        order = Order.objects.filter(customer_id=customer_id)
        return order


class ProductImageVeiwSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


class OrderPaymentWebHook(APIView):
    # TODO: verify origin of request

    def post(self, request, *args, **kwargs):
        data = request.data.get('data', {})
        transaction_reference = data.get('reference')
        amount = data.get('amount', 0)
        customer_data = data.get('customer')
        customer_email = customer_data.get('email')

        if data.get('status') != 'success':
            return Response({'success': False}, status=400)

        paystack_verification_url = f"https://api.paystack.co/transaction/verify/{transaction_reference}"
        headers = {
            "Authorization": f"Bearer: {prod.PAYSTACK_SECRET_KEY}"
        }
        response = requests.get(paystack_verification_url)
        response_data = response.json()
        verification_data = response_data.get('data', {})
        verification_customer = verification_data.get('customer', {})
        verification_customer_email = verification_customer.get('email')

        if verification_data.get('status') != 'success' or amount < verification_data.get('amount') or \
                verification_customer_email != customer_email:
            return Response({'success': False}, status=400)

        order = Order.objects.filter(paystack_transaction_reference=transaction_reference).first()
        # TODO: make correction here in case you can filter email from Customer directly
        user = User.objects.filter(email=customer_email).first()
        customer = Customer.objects.filter(user=user).first()

        if not (order and customer):
            return Response({'success': False}, status=400)

        # TODO: Add transaction model and store reference in it. So users can see how payments flow.

        # set order as completed
        order.payment_status = 'C'
        order.placed_at = datetime.utcnow()
        order.save()
        return Response({'success': True})
