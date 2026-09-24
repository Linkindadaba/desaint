import os
import django
from decimal import Decimal

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from catalog.models import Product
from inventory.models import Supplier, InventoryItem, StockMovement


def seed_inventory():
    print("Seeding Inventory Engine for Desaint Stationeries...")

    admin_user = User.objects.filter(is_superuser=True).first()

    # 1. Seed Suppliers
    supp_desaint, _ = Supplier.objects.get_or_create(
        name="Desaint Print & Manufacturing Works Ltd",
        defaults={
            'contact_person': 'Kwame Antwi-Boasiako (Head of Production)',
            'phone': '+233 24 456 7890',
            'email': 'production@desaintstationeries.com',
            'address': 'Plot 14, Sunyani Light Industrial Area, Sunyani, Bono Region',
            'is_active': True
        }
    )

    supp_paper, _ = Supplier.objects.get_or_create(
        name="Accra Paper & Board Converters Ltd",
        defaults={
            'contact_person': 'Mrs. Faustina Mensah (Supply Lead)',
            'phone': '+233 20 812 3456',
            'email': 'orders@accrapaperconverters.com.gh',
            'address': 'Graphic Road, South Industrial Area, Accra',
            'is_active': True
        }
    )

    supp_tools, _ = Supplier.objects.get_or_create(
        name="Universal Stationery & Educational Tools Ltd",
        defaults={
            'contact_person': 'Ahmed Alhassan',
            'phone': '+233 26 998 7766',
            'email': 'import@universalstationerygh.com',
            'address': 'Warehouse Complex 4B, Tema Port Free Zones, Greater Accra',
            'is_active': True
        }
    )

    # 2. Inventory Items per Catalog Product
    # Mapping SKU to packaging details, costs, stock counts, and locations
    catalog_configs = {
        'DSP-EX-80': {
            'supplier': supp_desaint,
            'cost_price': Decimal('2.20'),
            'bulk_unit_name': 'Box',
            'retail_unit_name': 'Book',
            'pieces_per_carton': 120,
            'carton_stock': 35,
            'loose_stock': 120,
            'low_stock_threshold_cartons': 5,
            'low_stock_threshold_loose': 24,
            'warehouse_location': 'Sunyani Main Hub — Bay A-01 (Exercise Books)',
        },
        'DSP-NT-160': {
            'supplier': supp_desaint,
            'cost_price': Decimal('6.80'),
            'bulk_unit_name': 'Carton',
            'retail_unit_name': 'Book',
            'pieces_per_carton': 48,
            'carton_stock': 25,
            'loose_stock': 48,
            'low_stock_threshold_cartons': 4,
            'low_stock_threshold_loose': 12,
            'warehouse_location': 'Sunyani Main Hub — Bay A-03 (Hardcovers)',
        },
        'DSP-KG-GRID': {
            'supplier': supp_desaint,
            'cost_price': Decimal('3.10'),
            'bulk_unit_name': 'Pack',
            'retail_unit_name': 'Book',
            'pieces_per_carton': 50,
            'carton_stock': 12,
            'loose_stock': 50,
            'low_stock_threshold_cartons': 3,
            'low_stock_threshold_loose': 10,
            'warehouse_location': 'Sunyani Main Hub — Bay B-02 (Pre-School)',
        },
        'DSP-PPR-A4': {
            'supplier': supp_paper,
            'cost_price': Decimal('175.00'),
            'bulk_unit_name': 'Box (5 Reams)',
            'retail_unit_name': 'Ream',
            'pieces_per_carton': 5,
            'carton_stock': 80,
            'loose_stock': 20,
            'low_stock_threshold_cartons': 10,
            'low_stock_threshold_loose': 5,
            'warehouse_location': 'Sunyani Central Warehouse — Pallet Bay C-01',
        },
        'DSP-MRK-12': {
            'supplier': supp_tools,
            'cost_price': Decimal('26.00'),
            'bulk_unit_name': 'Carton (24 Packs)',
            'retail_unit_name': 'Box (12 Pens)',
            'pieces_per_carton': 24,
            'carton_stock': 15,
            'loose_stock': 24,
            'low_stock_threshold_cartons': 2,
            'low_stock_threshold_loose': 6,
            'warehouse_location': 'Sunyani Main Hub — Shelf D-04 (Instruments)',
        },
        'DSP-MTH-SET': {
            'supplier': supp_tools,
            'cost_price': Decimal('8.00'),
            'bulk_unit_name': 'Carton',
            'retail_unit_name': 'Set (Tin)',
            'pieces_per_carton': 60,
            'carton_stock': 20,
            'loose_stock': 60,
            'low_stock_threshold_cartons': 3,
            'low_stock_threshold_loose': 15,
            'warehouse_location': 'Sunyani Main Hub — Shelf D-02 (Geometry)',
        },
    }

    for sku, cfg in catalog_configs.items():
        try:
            prod = Product.objects.get(sku=sku)
            inv, created = InventoryItem.objects.get_or_create(
                product=prod,
                defaults={
                    'supplier': cfg['supplier'],
                    'cost_price': cfg['cost_price'],
                    'bulk_unit_name': cfg['bulk_unit_name'],
                    'retail_unit_name': cfg['retail_unit_name'],
                    'pieces_per_carton': cfg['pieces_per_carton'],
                    'carton_stock': cfg['carton_stock'],
                    'loose_stock': cfg['loose_stock'],
                    'low_stock_threshold_cartons': cfg['low_stock_threshold_cartons'],
                    'low_stock_threshold_loose': cfg['low_stock_threshold_loose'],
                    'warehouse_location': cfg['warehouse_location']
                }
            )

            if created:
                inv.sync_to_catalog()
                # Create initial balance stock movement
                StockMovement.objects.create(
                    item=inv,
                    movement_type='RESTOCK_IN',
                    carton_delta=cfg['carton_stock'],
                    loose_delta=cfg['loose_stock'],
                    resulting_carton_stock=cfg['carton_stock'],
                    resulting_loose_stock=cfg['loose_stock'],
                    reference='INIT-STOCK-BAL',
                    created_by=admin_user,
                    note=f"Initial warehouse stock valuation & onboarding for {prod.name}."
                )
                print(f" [CREATED] Inventory record for: {prod.name} ({inv.total_retail_pieces} effective units)")
            else:
                print(f" [EXISTS] Inventory record for: {prod.name}")

        except Product.DoesNotExist:
            print(f" [WARN] Product with SKU {sku} not found.")

    print("\nInventory seeding successfully completed.")


if __name__ == '__main__':
    seed_inventory()
