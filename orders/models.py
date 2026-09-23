from django.db import models
from decimal import Decimal

class POSSale(models.Model):
    PAYMENT_CHOICES = [
        ('CASH', 'Cash Counter'),
        ('MOMO_TILL', 'MTN Mobile Money Till'),
        ('TELECEL_CASH', 'Telecel Cash'),
        ('OTHER', 'Other'),
    ]

    receipt_number = models.CharField(max_length=50, unique=True, help_text='e.g. DSP-POS-1092')
    cashier_name = models.CharField(max_length=100, default='Solomon')
    store_branch = models.CharField(max_length=100, default='Sunyani Main Branch')
    payment_mode = models.CharField(max_length=25, choices=PAYMENT_CHOICES, default='CASH')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_tendered = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    change_given = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    items_summary = models.TextField(help_text='JSON or plain summary of items sold')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Counter POS Sale'
        verbose_name_plural = 'Sunyani Counter POS Sales'

    def __str__(self):
        return f"{self.receipt_number} — GH₵ {self.total_amount} ({self.payment_mode})"

    @property
    def parsed_items(self):
        import json
        try:
            items = json.loads(self.items_summary)
            result = []
            for item in items:
                qty = int(item.get('qty', 1))
                price = Decimal(str(item.get('price', 0)))
                line_total = Decimal(str(item.get('total', qty * price)))
                result.append({
                    'name': item.get('name', 'Stationery Item'),
                    'unit': item.get('unit', 'Piece'),
                    'qty': qty,
                    'price': price,
                    'line_total': line_total,
                })
            return result
        except Exception:
            return [{
                'name': self.items_summary or 'General Counter Sale',
                'unit': 'Item',
                'qty': 1,
                'price': self.total_amount,
                'line_total': self.total_amount,
            }]
