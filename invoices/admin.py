from django.contrib import admin
from .models import Invoice, InvoiceItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'invoice_type', 'tax_mode', 'client_name', 'subtotal', 'wht_amount', 'total_payable', 'payment_method', 'is_paid', 'created_at']
    list_filter = ['invoice_type', 'tax_mode', 'payment_method', 'is_paid']
    search_fields = ['invoice_number', 'client_name', 'client_phone', 'payment_reference']
    inlines = [InvoiceItemInline]
    readonly_fields = ['created_at']
    fieldsets = (
        ('Invoice Header', {
            'fields': ('invoice_number', 'invoice_type', 'tax_mode', 'client_name', 'client_phone', 'client_tin')
        }),
        ('Tax Calculation & Balances', {
            'fields': ('subtotal', 'vat_amount', 'wht_amount', 'total_payable')
        }),
        ('Payment Rails', {
            'fields': ('payment_method', 'is_paid', 'paid_at', 'payment_reference', 'notes')
        }),
        ('Audit Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
