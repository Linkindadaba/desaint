from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon_class', 'display_order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['display_order', 'is_active']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'retail_price', 'wholesale_price', 'wholesale_box_size', 'stock_status', 'is_customizable', 'is_active']
    list_filter = ['stock_status', 'category', 'is_customizable', 'is_active']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['retail_price', 'wholesale_price', 'stock_status', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Product Identification', {
            'fields': ('name', 'slug', 'category', 'sku', 'description', 'icon_class', 'image')
        }),
        ('Pricing & Wholesale Specifications', {
            'fields': ('retail_price', 'wholesale_price', 'wholesale_box_size')
        }),
        ('Warehouse & Customer Policy', {
            'description': 'Customer Display Policy: Never expose exact counts on storefront. Use stock_status badges.',
            'fields': ('stock_status', 'stock_quantity', 'is_customizable', 'is_active')
        }),
        ('Audit Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
