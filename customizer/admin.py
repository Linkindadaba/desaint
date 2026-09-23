from django.contrib import admin
from .models import RulingOption, CustomBookOrder

@admin.register(RulingOption)
class RulingOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'page_count', 'base_unit_price', 'is_popular', 'is_active']
    list_filter = ['category', 'is_popular', 'is_active']
    list_editable = ['base_unit_price', 'is_popular', 'is_active']
    search_fields = ['name']


@admin.register(CustomBookOrder)
class CustomBookOrderAdmin(admin.ModelAdmin):
    list_display = ['order_ref', 'school_name', 'ruling', 'quantity', 'unit_price', 'gross_amount', 'wht_deducted', 'net_payable', 'status', 'digital_proof_approved']
    list_filter = ['status', 'digital_proof_approved', 'ruling']
    search_fields = ['order_ref', 'school_name', 'proprietor_name', 'contact_phone']
    readonly_fields = ['gross_amount', 'wht_deducted', 'net_payable', 'plate_setup_fee', 'created_at', 'updated_at']
    fieldsets = (
        ('Contract Reference & Institution', {
            'fields': ('order_ref', 'school_name', 'proprietor_name', 'contact_phone', 'contact_email', 'delivery_location')
        }),
        ('Exercise Book Specifications', {
            'fields': ('ruling', 'quantity', 'unit_price', 'plate_setup_fee', 'school_crest', 'back_cover_content')
        }),
        ('Ghana Tax & Invoicing (Act 896)', {
            'description': 'Automated 3% Withholding Tax deduction on institutional goods procurement.',
            'fields': ('gross_amount', 'wht_rate', 'wht_deducted', 'net_payable')
        }),
        ('Digital Proof & Workflow Status', {
            'fields': ('status', 'digital_proof_approved', 'approved_by_signatory', 'approval_timestamp', 'notes')
        }),
        ('Audit Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
