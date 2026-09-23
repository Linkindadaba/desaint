from django.db import models
from decimal import Decimal

class SchoolCreditRecord(models.Model):
    STATUS_CHOICES = [
        ('CURRENT', 'Current / In Good Standing'),
        ('PARTIALLY_PAID', 'Partially Paid'),
        ('FULLY_SETTLED', 'Fully Settled'),
        ('OVERDUE_NOTICE', 'Overdue Notice Issued'),
    ]

    school_name = models.CharField(max_length=200)
    location = models.CharField(max_length=150, default='Sunyani')
    principal_name = models.CharField(max_length=150, help_text='Headmaster or Bursar name')
    phone_number = models.CharField(max_length=50)
    academic_term = models.CharField(max_length=100, default='Term 1 (2026/2027 Academic Year)')
    total_credit_granted = models.DecimalField(max_digits=12, decimal_places=2, help_text='Total invoiced on credit in GH₵')
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), help_text='Total installments received in GH₵')
    balance_outstanding = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), help_text='Remaining debt balance')
    term_due_date = models.DateField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='CURRENT')
    last_payment_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-balance_outstanding']
        verbose_name = 'School Credit Record'
        verbose_name_plural = 'School Credit & Receivables Ledger'

    def __str__(self):
        return f"{self.school_name} — Due: GH₵ {self.balance_outstanding}"

    def save(self, *args, **kwargs):
        self.balance_outstanding = self.total_credit_granted - self.amount_paid
        if self.balance_outstanding <= Decimal('0.00'):
            self.status = 'FULLY_SETTLED'
        elif self.amount_paid > Decimal('0.00'):
            self.status = 'PARTIALLY_PAID'
        super().save(*args, **kwargs)


class RegionalWaybill(models.Model):
    CARRIER_CHOICES = [
        ('VIP_JEOUN', 'VIP Jeoun Transport'),
        ('OA_TRAVEL', 'OA Travel and Tours'),
        ('IMPERIAL_EXPRESS', 'Imperial Express'),
        ('METRO_MASS', 'Metro Mass Transit (MMT)'),
        ('CAMPUS_VAN', 'Direct Campus Delivery Van'),
    ]

    STATUS_CHOICES = [
        ('BOOKED', 'Booked at Sunyani Terminal'),
        ('IN_TRANSIT', 'In Transit on Route'),
        ('ARRIVED_AT_TERMINAL', 'Arrived at Destination Terminal'),
        ('DELIVERED_AND_SIGNED', 'Delivered & Consignment Signed'),
    ]

    waybill_number = models.CharField(max_length=50, unique=True, help_text='e.g. VIP-SNY-8841')
    carrier = models.CharField(max_length=30, choices=CARRIER_CHOICES, default='VIP_JEOUN')
    origin_hub = models.CharField(max_length=100, default='Sunyani Main Hub')
    destination_town = models.CharField(max_length=100, help_text='e.g. Kumasi (Asafo), Tamale, Takoradi')
    recipient_name = models.CharField(max_length=150, help_text='Institution or Bookshop contact')
    recipient_phone = models.CharField(max_length=50)
    consignment_summary = models.CharField(max_length=255, help_text='e.g. 12 Heavy Cartons of 80pg Exercise Books')
    driver_conductor_name = models.CharField(max_length=150, blank=True)
    driver_phone = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='BOOKED')
    sms_alert_sent = models.BooleanField(default=False)
    dispatched_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-dispatched_at']
        verbose_name = 'Regional Bus Waybill'
        verbose_name_plural = 'Bus Waybill & Regional Dispatch Tracker'

    def __str__(self):
        return f"{self.waybill_number} ({self.carrier}) ➔ {self.destination_town}"
