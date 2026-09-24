from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import json

from catalog.models import Category, Product
from inventory.models import InventoryItem, Supplier
from orders.models import POSSale
from invoices.models import Invoice


class OrdersAndPOSTestCase(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='cashier_alice',
            password='testpassword123',
            is_staff=True,
            is_superuser=True
        )
        self.client = Client()
        self.client.login(username='cashier_alice', password='testpassword123')

        self.category = Category.objects.create(name='Office Paper', slug='office-paper')
        self.product = Product.objects.create(
            name='A4 Copy Paper 80gsm Box',
            slug='a4-copy-paper-80gsm-box',
            category=self.category,
            sku='DSP-A4-80',
            retail_price=Decimal('280.00'),
            wholesale_price=Decimal('260.00'),
            wholesale_box_size='Box of 5 Reams',
            stock_quantity=100
        )

        self.supplier = Supplier.objects.create(
            name='Paper Mills Ghana Ltd',
            phone='+233 24 111 3333'
        )

        self.inv = InventoryItem.objects.create(
            product=self.product,
            supplier=self.supplier,
            cost_price=Decimal('220.00'),
            bulk_unit_name='Box',
            retail_unit_name='Ream',
            pieces_per_carton=5,
            carton_stock=10,
            loose_stock=5
        )

        self.pos_sale = POSSale.objects.create(
            receipt_number='DSP-POS-9988',
            cashier_name='Alice',
            store_branch='Sunyani Main Branch',
            payment_mode='CASH',
            subtotal=Decimal('280.00'),
            tax_amount=Decimal('0.00'),
            total_amount=Decimal('280.00'),
            amount_tendered=Decimal('300.00'),
            change_given=Decimal('20.00'),
            items_summary=json.dumps([{'name': 'A4 Copy Paper', 'qty': 1, 'price': 280.0, 'unit': 'Box'}])
        )

    def test_cart_add_and_detail(self):
        """Customer can add a product to cart and view cart summary."""
        anon_client = Client()
        response = anon_client.post(
            reverse('orders_public:cart_add', kwargs={'product_id': self.product.id}),
            data={'quantity': 2},
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        # Check cart detail page
        detail_resp = anon_client.get(reverse('orders_public:cart_detail'))
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, 'A4 Copy Paper 80gsm Box')
        self.assertContains(detail_resp, '560.00')

    def test_cart_remove(self):
        """Customer can remove an item from their cart."""
        anon_client = Client()
        anon_client.post(
            reverse('orders_public:cart_add', kwargs={'product_id': self.product.id}),
            data={'quantity': 1}
        )
        remove_resp = anon_client.post(
            reverse('orders_public:cart_remove', kwargs={'product_id': self.product.id}),
            follow=True
        )
        self.assertEqual(remove_resp.status_code, 200)
        self.assertNotContains(remove_resp, '560.00')

    def test_checkout_and_inventory_deduction(self):
        """Customer checkout creates an Invoice, deducts warehouse inventory, and redirects to confirmation."""
        anon_client = Client()
        anon_client.post(
            reverse('orders_public:cart_add', kwargs={'product_id': self.product.id}),
            data={'quantity': 2}
        )

        data = {
            'client_name': 'Kofi Mensah Educational Services',
            'client_phone': '024 123 9999',
            'delivery_address': 'Sunyani Post Office Box 12',
            'channel_type': 'RETAIL_RECEIPT',
            'payment_method': 'MOMO_TILL',
            'notes': 'Call on delivery arrival.',
        }
        checkout_resp = anon_client.post(reverse('orders_public:checkout'), data=data, follow=True)
        self.assertEqual(checkout_resp.status_code, 200)

        # Verify invoice created
        inv_record = Invoice.objects.get(client_name='Kofi Mensah Educational Services')
        self.assertEqual(inv_record.subtotal, Decimal('560.00'))
        self.assertEqual(inv_record.payment_method, 'MOMO_TILL')

        # Verify inventory deduction: loose was 5, 2 deducted -> 3 left
        self.inv.refresh_from_db()
        self.assertEqual(self.inv.loose_stock, 3)

    def test_pos_terminal_view(self):
        """Cashier can access the Sunyani POS Terminal."""
        response = self.client.get(reverse('orders:pos_terminal'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'POS Terminal')
        self.assertContains(response, 'A4 Copy Paper 80gsm Box')

    def test_pos_history_view(self):
        """Cashier can view POS history and previous till receipts."""
        response = self.client.get(reverse('orders:pos_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'DSP-POS-9988')
        self.assertContains(response, '280.00')

    def test_pos_receipt_standalone_view(self):
        """Standalone receipt URL renders clean 80mm printable layout (Rule 6)."""
        response = self.client.get(reverse('orders:pos_receipt', kwargs={'pk': self.pos_sale.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'DSP-POS-9988')
        self.assertContains(response, 'GH₵ 280.00')
        self.assertContains(response, 'Change Returned')
