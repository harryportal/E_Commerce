from django.contrib import admin
from . import models
from django.db.models.aggregates import Count

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title','products_count']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        return collection.products_count

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .annotate(products_count=Count('product')).all()

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    #autocomplete_fields = ['collection']
    list_display = ['title','unit_price', 'inventory_status']
    list_editable = ['unit_price']
    list_per_page = 10
    list_select_related = ['collection']
    list_filter = ['collection','last_update']
    prepopulated_fields = {
        'slug':['title']
    }

    # adding a computed column
    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'LOW'
        else:
            return 'HIGH'


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ['first_name','last_name','membership']
    list_editable = ['membership']
    search_fields = ['first_name','last_name']

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['placed_at','payment_status','customer']
    list_per_page = 10
