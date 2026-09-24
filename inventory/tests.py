from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import json

from catalog.models import Category, Product
from inventory.models import Supplier, InventoryItem, StockMovement
from orders.models import POSSale


class InventoryEngineTestCase(TestCase):
    def setUp(self):
        # Create staff user with cashier role
        self.staff_user = User.objects.create_user(
            username='inventory_officer',
            password='testpassword123',
            is_staff=True,
            is_superuser=True
        )
        self.client = Client()
        self.client.login(username='inventory_officer', password='testpassword123')

        # Create Category and Product
        self.category = Category.objects.create(
            name="Exercise Books",
            slug="exercise-books"
        )
        self.product = Product.objects.create(
            name="Desaint Premium Exercise Book",
            slug="desaint-premium-exercise-book",
            category=self.category,
            sku="DSP-TEST-01",
            retail_price=Decimal('5.00'),
            wholesale_price=Decimal('4.00'),
            wholesale_box_size="Box of 100",
            stock_quantity=1000
        )

        # Create Supplier
        self.supplier = Supplier.objects.create(
            name="Desaint Mill Works",
            phone="+233 24 111 2222"
        )

        # Create Inventory Item: 10 boxes (100 pcs/box = 1000 pcs) + 20 loose = 1020 pcs
        self.inv = InventoryItem.objects.create(
            product=self.product,
            supplier=self.supplier,
            cost_price=Decimal('2.50'),
            bulk_unit_name="Box",
            retail_unit_name="Book",
            pieces_per_carton=100,
            carton_stock=10,
            loose_stock=20,
            low_stock_threshold_cartons=2,
            low_stock_threshold_loose=10
        )

    def test_inventory_computed_properties(self):
        """Test effective pieces and valuation calculations."""
        # 10 * 100 + 20 = 1020
        self.assertEqual(self.inv.total_retail_pieces, 1020)
        # 1020 * 2.50 = 2550.00
        self.assertEqual(self.inv.total_cost_valuation, Decimal('2550.00'))
        # Not low stock since carton_stock=10 > 2
        self.assertFalse(self.inv.is_low_stock)
        self.assertEqual(self.inv.stock_status_label, "IN_STOCK")

    def test_loose_sale_without_unbox(self):
        """Selling loose pieces when enough shelf stock exists."""
        self.inv.fulfill_and_deduct(quantity=5, is_carton=False, user=self.staff_user, reference='POS-001')
        self.inv.refresh_from_db()

        self.assertEqual(self.inv.loose_stock, 15)
        self.assertEqual(self.inv.carton_stock, 10)
        self.assertEqual(self.inv.total_retail_pieces, 1015)

        # Check movement record
        mov = StockMovement.objects.filter(item=self.inv).latest('created_at')
        self.assertEqual(mov.movement_type, 'POS_SALE')
        self.assertEqual(mov.loose_delta, -5)
        self.assertEqual(mov.carton_delta, 0)
        self.assertEqual(mov.resulting_loose_stock, 15)

    def test_loose_sale_with_automatic_break_bulk(self):
        """Selling more than loose shelf stock triggers auto unboxing from sealed cartons."""
        # Initial loose: 20. Sell 50 -> Deficit is 30.
        # 1 box has 100 pieces. Auto-unboxing opens 1 box.
        # Carton stock becomes 10 - 1 = 9.
        # Loose stock becomes 20 + 100 - 50 = 70.
        self.inv.fulfill_and_deduct(quantity=50, is_carton=False, user=self.staff_user, reference='POS-002')
        self.inv.refresh_from_db()

        self.assertEqual(self.inv.carton_stock, 9)
        self.assertEqual(self.inv.loose_stock, 70)
        self.assertEqual(self.inv.total_retail_pieces, 970)

        # Check that both BREAK_BULK and POS_SALE movements were created
        movements = StockMovement.objects.filter(item=self.inv).order_by('-created_at')
        self.assertEqual(movements.count(), 2)

        sale_mov = movements[0]
        self.assertEqual(sale_mov.movement_type, 'POS_SALE')
        self.assertEqual(sale_mov.loose_delta, -50)

        unbox_mov = movements[1]
        self.assertEqual(unbox_mov.movement_type, 'BREAK_BULK')
        self.assertEqual(unbox_mov.carton_delta, -1)
        self.assertEqual(unbox_mov.loose_delta, 100)

    def test_wholesale_carton_sale(self):
        """Selling bulk cartons directly."""
        self.inv.fulfill_and_deduct(quantity=3, is_carton=True, user=self.staff_user, reference='WHOLESALE-01')
        self.inv.refresh_from_db()

        self.assertEqual(self.inv.carton_stock, 7)
        self.assertEqual(self.inv.loose_stock, 20)
        self.assertEqual(self.inv.total_retail_pieces, 720)

    def test_restock(self):
        """Receiving incoming shipment."""
        self.inv.restock(cartons=5, loose_pieces=10, cost_price=Decimal('2.60'), user=self.staff_user, reference='WB-999')
        self.inv.refresh_from_db()

        self.assertEqual(self.inv.carton_stock, 15)
        self.assertEqual(self.inv.loose_stock, 30)
        self.assertEqual(self.inv.cost_price, Decimal('2.60'))

        mov = StockMovement.objects.filter(item=self.inv).latest('created_at')
        self.assertEqual(mov.movement_type, 'RESTOCK_IN')
        self.assertEqual(mov.carton_delta, 5)
        self.assertEqual(mov.loose_delta, 10)

    def test_physical_adjustment(self):
        """Stocktake variance audit adjustment."""
        self.inv.adjust_stock(new_carton_count=8, new_loose_count=18, reason="Monthly Stocktake", user=self.staff_user)
        self.inv.refresh_from_db()

        self.assertEqual(self.inv.carton_stock, 8)
        self.assertEqual(self.inv.loose_stock, 18)

        mov = StockMovement.objects.filter(item=self.inv).latest('created_at')
        self.assertEqual(mov.movement_type, 'ADJUSTMENT')
        self.assertEqual(mov.carton_delta, -2) # was 10, now 8
        self.assertEqual(mov.loose_delta, -2)  # was 20, now 18

    def test_pos_submit_sale_integration(self):
        """End-to-end POS submission deducting inventory."""
        url = reverse('orders:pos_submit_sale')
        payload = {
            'items': [
                {
                    'id': f"{self.product.id}-ret",
                    'name': self.product.name,
                    'price': 5.0,
                    'unit': 'Piece',
                    'qty': 2
                }
            ],
            'total_amount': '10.00',
            'amount_tendered': '10.00',
            'change_given': '0.00',
            'payment_mode': 'CASH',
            'cashier_name': 'Test Cashier'
        }

        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        self.assertTrue(resp_data['success'])

        # Verify inventory deduction
        self.inv.refresh_from_db()
        self.assertEqual(self.inv.loose_stock, 18) # 20 - 2 = 18

    def test_supplier_edit(self):
        """Staff can edit supplier details."""
        url = reverse('inventory:edit_supplier', kwargs={'pk': self.supplier.pk})
        data = {
            'name': 'Desaint Mill Works International',
            'contact_person': 'Kwame Mensah',
            'phone': '+233 24 999 8888',
            'email': 'supply@desaintmill.com',
            'address': 'Sunyani Industrial Area, Plot 42',
            'is_active': 'on',
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        self.supplier.refresh_from_db()
        self.assertEqual(self.supplier.name, 'Desaint Mill Works International')
        self.assertEqual(self.supplier.phone, '+233 24 999 8888')
        self.assertEqual(self.supplier.contact_person, 'Kwame Mensah')

    def test_supplier_delete(self):
        """CEO can remove supplier."""
        pk = self.supplier.pk
        url = reverse('inventory:delete_supplier', kwargs={'pk': pk})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Supplier.objects.filter(pk=pk).exists())

    def test_item_config_edit(self):
        """Staff can update inventory packaging ratio and unit cost without altering physical stock."""
        url = reverse('inventory:edit_config', kwargs={'pk': self.inv.pk})
        data = {
            'cost_price': '3.10',
            'pieces_per_carton': '144',
            'bulk_unit_name': 'Carton',
            'retail_unit_name': 'Piece',
            'low_stock_threshold_cartons': '5',
            'warehouse_location': 'Bay 2 - Section C',
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        self.inv.refresh_from_db()
        self.assertEqual(self.inv.cost_price, Decimal('3.10'))
        self.assertEqual(self.inv.pieces_per_carton, 144)
        self.assertEqual(self.inv.bulk_unit_name, 'Carton')
        self.assertEqual(self.inv.low_stock_threshold_cartons, 5)
        self.assertEqual(self.inv.warehouse_location, 'Bay 2 - Section C')
        # Stock balances remain intact
        self.assertEqual(self.inv.carton_stock, 10)
        self.assertEqual(self.inv.loose_stock, 20)

