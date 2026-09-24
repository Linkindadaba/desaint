import math
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Supplier(models.Model):
    name = models.CharField(max_length=150, unique=True, help_text="Company or distributor name")
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True, help_text="Warehouse location or supply depot")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    product = models.OneToOneField(
        'catalog.Product',
        on_delete=models.CASCADE,
        related_name='inventory',
        help_text="Associated product in the public and wholesale catalog"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_items'
    )
    
    # Financials & Valuation
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Unit manufacturing or landed procurement cost per retail piece (GH₵)"
    )
    
    # Packaging Hierarchy
    bulk_unit_name = models.CharField(
        max_length=50,
        default="Carton",
        help_text="Wholesale bulk packaging title (e.g. Carton, Box, Pack)"
    )
    retail_unit_name = models.CharField(
        max_length=50,
        default="Piece",
        help_text="Individual retail shelf unit title (e.g. Book, Piece, Ream)"
    )
    pieces_per_carton = models.PositiveIntegerField(
        default=120,
        help_text="Number of loose retail units contained inside 1 sealed bulk carton/box"
    )
    
    # Real-Time Warehouse & Shelf Balances
    carton_stock = models.PositiveIntegerField(
        default=0,
        help_text="Sealed bulk cartons currently in warehouse storage"
    )
    loose_stock = models.PositiveIntegerField(
        default=0,
        help_text="Loose shelf pieces available for direct walk-in retail counter sales"
    )
    
    # Reorder Thresholds & Safety Stock
    low_stock_threshold_cartons = models.PositiveIntegerField(
        default=3,
        help_text="Minimum sealed bulk cartons before triggering warehouse restock alert"
    )
    low_stock_threshold_loose = models.PositiveIntegerField(
        default=15,
        help_text="Minimum shelf pieces before triggering auto break-bulk unbox alert"
    )
    warehouse_location = models.CharField(
        max_length=100,
        default="Sunyani Main Hub — Shelf A1",
        help_text="Physical shelf, bay, or room location in Sunyani warehouse"
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['product__category__name', 'product__name']
        verbose_name = "Inventory Item & Stock Balance"
        verbose_name_plural = "Inventory Items & Stock Balances"

    def __str__(self):
        return f"{self.product.name} ({self.carton_stock} {self.bulk_unit_name}s + {self.loose_stock} {self.retail_unit_name}s)"

    # ── Computed Properties ──────────────────────────────────────────────────
    @property
    def total_retail_pieces(self):
        """Total effective sellable loose pieces combining sealed cartons and shelf stock."""
        return (self.carton_stock * self.pieces_per_carton) + self.loose_stock

    @property
    def total_cost_valuation(self):
        """Current total capital tied up in inventory at cost price."""
        return Decimal(str(self.total_retail_pieces)) * self.cost_price

    @property
    def total_retail_valuation(self):
        """Estimated revenue yield if all current inventory is sold."""
        loose_val = Decimal(str(self.loose_stock)) * self.product.retail_price
        carton_val = Decimal(str(self.carton_stock)) * self.product.wholesale_price
        return loose_val + carton_val

    @property
    def is_low_stock(self):
        """Flags whether current stock is critically low and requires procurement."""
        return (
            self.carton_stock <= self.low_stock_threshold_cartons and
            self.loose_stock <= self.low_stock_threshold_loose
        )

    @property
    def stock_status_label(self):
        """Internal stock status for cashier and management dashboards."""
        if self.total_retail_pieces == 0:
            return "OUT_OF_STOCK"
        elif self.is_low_stock:
            return "LOW_STOCK"
        return "IN_STOCK"

    # ── Core Stock Operations & Break-Bulk Engine ────────────────────────────
    def sync_to_catalog(self):
        """Syncs the computed authoritative stock count back to the catalog model."""
        self.product.stock_quantity = self.total_retail_pieces
        if self.total_retail_pieces > self.pieces_per_carton:
            self.product.stock_status = 'IN_STOCK'
        elif self.total_retail_pieces > 0:
            self.product.stock_status = 'AVAILABLE_ON_ORDER'
        else:
            self.product.stock_status = 'BACKORDER_ALLOWED'
        self.product.save(update_fields=['stock_quantity', 'stock_status', 'updated_at'])

    def fulfill_and_deduct(self, quantity, is_carton=False, user=None, reference='', note=''):
        """
        Deducts units for a POS sale, wholesale order, or dispatch.
        If selling loose shelf pieces and shelf count is low, automatically
        unboxes the needed cartons from warehouse stock and logs a BREAK_BULK movement.
        """
        quantity = int(quantity)
        if quantity <= 0:
            return

        if is_carton:
            # Wholesale carton sale
            actual_cartons_deducted = min(self.carton_stock, quantity)
            self.carton_stock = max(0, self.carton_stock - quantity)
            self.save(update_fields=['carton_stock', 'updated_at'])

            StockMovement.objects.create(
                item=self,
                movement_type='POS_SALE' if 'POS' in reference else 'B2B_SALE',
                carton_delta=-quantity,
                loose_delta=0,
                resulting_carton_stock=self.carton_stock,
                resulting_loose_stock=self.loose_stock,
                reference=reference or 'WHOLESALE-SALE',
                created_by=user,
                note=note or f"Sold {quantity} {self.bulk_unit_name}(s) of '{self.product.name}'."
            )
        else:
            # Retail loose piece sale
            # Auto-unbox from sealed cartons if loose shelf stock is insufficient
            if self.loose_stock < quantity and self.carton_stock > 0:
                deficit = quantity - self.loose_stock
                boxes_to_open = min(
                    math.ceil(deficit / self.pieces_per_carton),
                    self.carton_stock
                )
                if boxes_to_open > 0:
                    unboxed_pieces = boxes_to_open * self.pieces_per_carton
                    self.carton_stock -= boxes_to_open
                    self.loose_stock += unboxed_pieces
                    self.save(update_fields=['carton_stock', 'loose_stock', 'updated_at'])

                    StockMovement.objects.create(
                        item=self,
                        movement_type='BREAK_BULK',
                        carton_delta=-boxes_to_open,
                        loose_delta=unboxed_pieces,
                        resulting_carton_stock=self.carton_stock,
                        resulting_loose_stock=self.loose_stock,
                        reference=reference or 'AUTO-UNBOX',
                        created_by=user,
                        note=f"Auto-unboxed {boxes_to_open} {self.bulk_unit_name}(s) into {unboxed_pieces} loose {self.retail_unit_name}(s) to fulfill sale."
                    )

            # Deduct loose pieces sold
            self.loose_stock = max(0, self.loose_stock - quantity)
            self.save(update_fields=['loose_stock', 'updated_at'])

            StockMovement.objects.create(
                item=self,
                movement_type='POS_SALE',
                carton_delta=0,
                loose_delta=-quantity,
                resulting_carton_stock=self.carton_stock,
                resulting_loose_stock=self.loose_stock,
                reference=reference or 'POS-SALE',
                created_by=user,
                note=note or f"Sold {quantity} {self.retail_unit_name}(s) of '{self.product.name}'."
            )

        self.sync_to_catalog()

    def restock(self, cartons=0, loose_pieces=0, cost_price=None, user=None, reference='', note=''):
        """Restocks inventory from supplier delivery or production run."""
        cartons = max(0, int(cartons))
        loose_pieces = max(0, int(loose_pieces))

        if cartons == 0 and loose_pieces == 0:
            return

        self.carton_stock += cartons
        self.loose_stock += loose_pieces

        if cost_price is not None and cost_price > Decimal('0.00'):
            self.cost_price = Decimal(str(cost_price))

        self.save(update_fields=['carton_stock', 'loose_stock', 'cost_price', 'updated_at'])

        StockMovement.objects.create(
            item=self,
            movement_type='RESTOCK_IN',
            carton_delta=cartons,
            loose_delta=loose_pieces,
            resulting_carton_stock=self.carton_stock,
            resulting_loose_stock=self.loose_stock,
            reference=reference or 'RESTOCK',
            created_by=user,
            note=note or f"Received {cartons} {self.bulk_unit_name}(s) and {loose_pieces} {self.retail_unit_name}(s) into Sunyani warehouse."
        )

        self.sync_to_catalog()

    def adjust_stock(self, new_carton_count, new_loose_count, reason="Stocktake Physical Count Audit", user=None, note=''):
        """Reconciles physical inventory count discrepancies with automatic variance logging."""
        new_carton_count = max(0, int(new_carton_count))
        new_loose_count = max(0, int(new_loose_count))

        c_delta = new_carton_count - self.carton_stock
        l_delta = new_loose_count - self.loose_stock

        if c_delta == 0 and l_delta == 0:
            return

        self.carton_stock = new_carton_count
        self.loose_stock = new_loose_count
        self.save(update_fields=['carton_stock', 'loose_stock', 'updated_at'])

        StockMovement.objects.create(
            item=self,
            movement_type='ADJUSTMENT',
            carton_delta=c_delta,
            loose_delta=l_delta,
            resulting_carton_stock=self.carton_stock,
            resulting_loose_stock=self.loose_stock,
            reference='STOCKTAKE',
            created_by=user,
            note=f"Variance Audit ({reason}): Cartons ({c_delta:+d}), Loose ({l_delta:+d}). {note}".strip()
        )

        self.sync_to_catalog()


class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('RESTOCK_IN', 'Restock / Supplier Inflow'),
        ('POS_SALE', 'Counter POS Sale Out'),
        ('B2B_SALE', 'B2B Wholesale Dispatch'),
        ('BREAK_BULK', 'Break-Bulk Unboxing (Carton → Shelf)'),
        ('ADJUSTMENT', 'Stocktake Physical Audit Adjustment'),
        ('DAMAGE', 'Damaged / Write-Off'),
        ('RETURN', 'Customer Return Restock'),
    ]

    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='movements'
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPES,
        default='POS_SALE'
    )
    carton_delta = models.IntegerField(
        default=0,
        help_text="Net change in bulk cartons (+ for restock, - for sale or unboxing)"
    )
    loose_delta = models.IntegerField(
        default=0,
        help_text="Net change in shelf pieces (+ for restock/unboxing, - for retail sale)"
    )
    resulting_carton_stock = models.PositiveIntegerField(
        help_text="Carton balance immediately after this movement"
    )
    resulting_loose_stock = models.PositiveIntegerField(
        help_text="Loose piece balance immediately after this movement"
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="POS Receipt #, Invoice #, or Waybill Reference"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Staff member who processed the transaction"
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Stock Movement Ledger Record"
        verbose_name_plural = "Stock Movement Ledger Records"

    def __str__(self):
        return f"[{self.get_movement_type_display()}] {self.item.product.name} (Carton: {self.carton_delta:+d}, Loose: {self.loose_delta:+d})"

    @property
    def badge_color(self):
        if self.movement_type in ['RESTOCK_IN', 'RETURN']:
            return 'success'
        elif self.movement_type in ['POS_SALE', 'B2B_SALE']:
            return 'danger'
        elif self.movement_type == 'BREAK_BULK':
            return 'info'
        elif self.movement_type == 'ADJUSTMENT':
            return 'warning'
        return 'secondary'

    @property
    def formatted_carton_delta(self):
        return f"{self.carton_delta:+d}"

    @property
    def formatted_loose_delta(self):
        return f"{self.loose_delta:+d}"
