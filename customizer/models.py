from django.db import models
from decimal import Decimal

class RulingOption(models.Model):
    CATEGORY_CHOICES = [
        ('EXERCISE', 'Standard Exercise Book'),
        ('NOTE', 'Note 1 & Note 3 Hardcover'),
        ('KINDERGARTEN', 'Pre-School & Kindergarten'),
        ('SPECIALIZED', 'Graph & Sketch Books'),
    ]

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='EXERCISE')
    page_count = models.PositiveIntegerField(default=80)
    base_unit_price = models.DecimalField(max_digits=8, decimal_places=2, help_text='Base price per copy in GH₵')
    description = models.CharField(max_length=255, blank=True)
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (GH₵ {self.base_unit_price})"


class CustomBookOrder(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft Quote'),
        ('PROOF_PENDING', 'Awaiting Digital Proof Approval'),
        ('PROOF_APPROVED', 'Approved by School Proprietor'),
        ('PLATE_MAKING', 'Offset Plate & Film Casting'),
        ('PRINTING', 'High-Speed Printing & Folding'),
        ('COMPLETED', 'Finished & Packaged'),
        ('DISPATCHED', 'Dispatched via Regional Bus / Van'),
    ]

    order_ref = models.CharField(max_length=40, unique=True, help_text='e.g. DSP-2026-STJ-0042')
    school_name = models.CharField(max_length=200)
    proprietor_name = models.CharField(max_length=150)
    contact_phone = models.CharField(max_length=50)
    contact_email = models.EmailField(blank=True)
    delivery_location = models.CharField(max_length=200, help_text='Campus or Bus terminal town')
    ruling = models.ForeignKey(RulingOption, on_delete=models.PROTECT, related_name='custom_orders')
    quantity = models.PositiveIntegerField(default=5000, help_text='MOQ enforced: 5,000 – 10,000 copies recommended')
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('3.20'))
    plate_setup_fee = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), help_text='Waived (0.00) for orders >= 1,000 copies')
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    wht_rate = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('3.00'), help_text='Statutory 3% GRA WHT Act 896')
    wht_deducted = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    net_payable = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    school_crest = models.ImageField(upload_to='crests/', blank=True, null=True)
    back_cover_content = models.TextField(default='School Anthem, School Rules & Regulations, National Pledge')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PROOF_PENDING')
    digital_proof_approved = models.BooleanField(default=False)
    approved_by_signatory = models.CharField(max_length=150, blank=True)
    approval_timestamp = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_ref} — {self.school_name} ({self.quantity:,} copies)"

    def save(self, *args, **kwargs):
        # Auto-compute financials
        if self.ruling:
            self.unit_price = self.ruling.base_unit_price
        # Free plate fee for >= 1,000 copies
        if self.quantity >= 1000:
            self.plate_setup_fee = Decimal('0.00')
        else:
            self.plate_setup_fee = Decimal('350.00')
        self.gross_amount = (Decimal(self.quantity) * self.unit_price) + self.plate_setup_fee
        self.wht_deducted = (self.gross_amount * (self.wht_rate / Decimal('100.00'))).quantize(Decimal('0.01'))
        self.net_payable = self.gross_amount - self.wht_deducted
        super().save(*args, **kwargs)
