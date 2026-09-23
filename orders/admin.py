from django.contrib import admin
from .models import POSSale

@admin.register(POSSale)
class POSSaleAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'cashier_name', 'store_branch', 'payment_mode', 'total_amount', 'created_at']
    list_filter = ['payment_mode', 'store_branch']
    search_fields = ['receipt_number', 'cashier_name', 'items_summary']
    readonly_fields = ['created_at']
