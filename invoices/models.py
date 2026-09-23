from django.db import models
from decimal import Decimal

class Invoice(models.Model):
    INVOICE_TYPE_CHOICES = [
        ('RETAIL_RECEIPT', 'Sunyani Counter Retail Receipt'),
        ('WHOLESALE_INVOICE', 'B2B Wholesale Commercial Invoice'),
        ('INSTITUTIONAL_PROFORMA', 'School Institutional Procurement Proforma'),
    ]

    TAX_MODE_CHOICES = [
        ('RETAIL_NET', 'Retail Mode (Net Flat)'),
        ('GRA_STANDARD_VAT', 'GRA Standard (15% VAT + 2.5% NHIL + 2.5% GETFund + 1% COVID)'),
        ('INSTITUTIONAL_WHT_3PCT', 'Institutional Mode (Act 896 3% WHT Deducted)'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash Counter'),
        ('MOMO_TILL', 'MTN Mobile Money Till'),
        ('TELECEL_CASH', 'Telecel Cash'),
        ('BANK_TRANSFER', 'GCB / Bank Transfer'),
        ('TERM_CREDIT', 'Institutional Term Credit (30-Day)'),
    ]

    invoice_number = models.CharField(max_length=50, unique=True, help_text='e.g. SIKA-DSP-2026-001')
    invoice_type = models.CharField(max_length=30, choices=INVOICE_TYPE_CHOICES, default='RETAIL_RECEIPT')
    tax_mode = models.CharField(max_length=30, choices=TAX_MODE_CHOICES, default='RETAIL_NET')
    client_name = models.CharField(max_length=200)
    client_phone = models.CharField(max_length=50, blank=True)
    client_tin = models.CharField(max_length=50, blank=True, help_text='GRA Tax Identification Number (TIN)')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    wht_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text='3% Withholding Tax deduction')
    total_payable = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    payment_method = models.CharField(max_length=25, choices=PAYMENT_METHOD_CHOICES, default='CASH')
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(blank=True, null=True)
    payment_reference = models.CharField(max_length=100, blank=True, help_text='MoMo Transaction ID or Bank Slip Ref')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice_number} — {self.client_name} (GH₵ {self.total_payable})"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.description} ({self.total_price})"

    def save(self, *args, **kwargs):
        self.total_price = Decimal(self.quantity) * self.unit_price
        super().save(*args, **kwargs)
