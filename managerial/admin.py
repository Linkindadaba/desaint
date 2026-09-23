from django.contrib import admin
from .models import SchoolCreditRecord, RegionalWaybill

@admin.register(SchoolCreditRecord)
class SchoolCreditRecordAdmin(admin.ModelAdmin):
    list_display = ['school_name', 'location', 'principal_name', 'phone_number', 'total_credit_granted', 'amount_paid', 'balance_outstanding', 'term_due_date', 'status']
    list_filter = ['status', 'location', 'academic_term']
    search_fields = ['school_name', 'principal_name', 'phone_number']
    readonly_fields = ['balance_outstanding', 'created_at', 'updated_at']
    fieldsets = (
        ('School & Authority Contact', {
            'fields': ('school_name', 'location', 'principal_name', 'phone_number', 'academic_term')
        }),
        ('Term Receivables Financials', {
            'fields': ('total_credit_granted', 'amount_paid', 'balance_outstanding', 'term_due_date', 'last_payment_date')
        }),
        ('Status & Management Notes', {
            'fields': ('status', 'notes')
        }),
        ('Audit Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RegionalWaybill)
class RegionalWaybillAdmin(admin.ModelAdmin):
    list_display = ['waybill_number', 'carrier', 'origin_hub', 'destination_town', 'recipient_name', 'recipient_phone', 'status', 'dispatched_at']
    list_filter = ['carrier', 'status', 'destination_town']
    search_fields = ['waybill_number', 'recipient_name', 'recipient_phone', 'driver_conductor_name']
    readonly_fields = ['dispatched_at']
    fieldsets = (
        ('Consignment & Carrier Identification', {
            'fields': ('waybill_number', 'carrier', 'origin_hub', 'destination_town', 'consignment_summary')
        }),
        ('Recipient Details', {
            'fields': ('recipient_name', 'recipient_phone')
        }),
        ('Driver / Conductor Contact', {
            'fields': ('driver_conductor_name', 'driver_phone')
        }),
        ('Dispatch Status & Tracking', {
            'fields': ('status', 'sms_alert_sent', 'delivered_at')
        }),
    )
