from .models import Product, Customer, Address, Collection, Cart, CartItem, Review, Order, OrderItem, ProductImage
from rest_framework import serializers
from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404

class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = ['id','image']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'slug', 'inventory', 'description', 'unit_price', 'price_with_tax', 'collection',
                  'images']

    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', ' title', 'products_count']

    products_count = serializers.IntegerField(read_only=True)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']

    def create(self, validated_data):
        product_id = self.context['product_id']  # the self.context contains context variables sent from the view
        return Review.objects.create(product_id=product_id, **validated_data)


class ProductCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['title', 'description', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductCartSerializer()
    cart_price = serializers.SerializerMethodField()

    def get_cart_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'cart_price']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_cart_price = serializers.SerializerMethodField()

    def get_total_cart_price(self, cart: Cart):
        total_price = [item.quantity * item.product.unit_price for item in cart.cart_items.all()]
        return sum(total_price)

    class Meta:
        model = Cart
        fields = ['id', 'cart_items', 'total_cart_price']


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No Associated Product with the given id ')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(product_id=product_id, cart_id=cart_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item

        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()

    class Meta:
        model = Customer
        fields = ['id', 'user_id','phone','birth_date', 'membership']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductCartSerializer()

    class Meta:
        model = OrderItem
        fields = ['id','product','quantity','unit_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id','placed_at','payment_status','customer', 'items']

class OrderCreateSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        """ check if cart exists or contain cart items """
        if not Cart.objects.filter(id=cart_id).exists():
            raise serializers.ValidationError(f'No cart with id {cart_id} was found')
        elif CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('Cart has no cart items')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            """ will execute all the database queries as a single transaction to avoid an inconsistent state in
            the case of database failure """
            # get the cart with the validated cart_id
            cart_id = self.validated_data['cart_id']

            cart = get_object_or_404(Cart, id=cart_id)

            # create an Order data to store all order items
            user_id = self.context['user_id']
            customer = Customer.objects.get(user_id=user_id)
            order = Order.objects.create(customer=customer)

            # get all the cart items from the cart
            cart_items = CartItem.objects.filter(cart_id=cart_id).select_related('product').all()

            # use a list comprehension to create an Order item for each cart item
            order_items = [OrderItem(order=order,
                                     product=item.product,
                                     quantity=item.quantity,
                                     unit_price=item.unit_price)
                           for item in cart_items]
            OrderItem.objects.bulk_create(order_items)
            cart.delete()
            return order

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']


