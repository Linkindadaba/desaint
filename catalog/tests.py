from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from catalog.models import Category, Product
from inventory.models import InventoryItem, Supplier


class CatalogCRUDTestCase(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='staff_manager',
            password='testpassword123',
            is_staff=True,
            is_superuser=True
        )
        self.client = Client()
        self.client.login(username='staff_manager', password='testpassword123')

        self.category = Category.objects.create(
            name='Notebooks & Writing',
            slug='notebooks-writing'
        )

        self.supplier = Supplier.objects.create(
            name='Accra Paper Converting Mill',
            phone='+233 24 555 6666'
        )

        self.product = Product.objects.create(
            name='Standard 80-Page Exercise Book',
            slug='standard-80-page-exercise-book',
            category=self.category,
            sku='DSP-EX-80',
            retail_price=Decimal('3.50'),
            wholesale_price=Decimal('350.00'),
            wholesale_box_size='Box of 120',
            stock_quantity=500
        )

    def test_product_list_view(self):
        """Staff can view product catalog page."""
        response = self.client.get(reverse('catalog:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Standard 80-Page Exercise Book')
        self.assertContains(response, 'DSP-EX-80')

    def test_product_create_with_inventory_onboarding(self):
        """Creating a product dynamically onboarded into warehouse inventory."""
        data = {
            'name': 'Hardcover Ledger 160-Page',
            'category': self.category.id,
            'sku': 'DSP-HD-160',
            'retail_price': '15.00',
            'wholesale_price': '120.00',
            'wholesale_box_size': 'Box of 10',
            'description': 'Bound hardcover journal for accounting',
            'icon_class': 'fas fa-book',
            'supplier_id': self.supplier.id,
            'cost_price': '9.50',
            'carton_stock': '5',
            'loose_stock': '20',
            'pieces_per_carton': '10',
            'warehouse_location': 'Bay 4 - Shelf B',
        }
        response = self.client.post(reverse('catalog:product_create'), data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Check product created
        prod = Product.objects.get(sku='DSP-HD-160')
        self.assertEqual(prod.name, 'Hardcover Ledger 160-Page')
        self.assertEqual(prod.retail_price, Decimal('15.00'))

        # Check inventory item auto-created
        inv = InventoryItem.objects.get(product=prod)
        self.assertEqual(inv.carton_stock, 5)
        self.assertEqual(inv.loose_stock, 20)
        self.assertEqual(inv.cost_price, Decimal('9.50'))
        self.assertEqual(inv.warehouse_location, 'Bay 4 - Shelf B')

    def test_product_edit(self):
        """Editing an existing product's retail and wholesale pricing."""
        data = {
            'name': 'Premium 80-Page Exercise Book (Edited)',
            'category': self.category.id,
            'retail_price': '4.20',
            'wholesale_price': '400.00',
            'wholesale_box_size': 'Box of 120',
            'stock_status': 'AVAILABLE_ON_ORDER',
            'is_customizable': 'on',
            'is_active': 'on',
        }
        response = self.client.post(
            reverse('catalog:product_edit', kwargs={'pk': self.product.pk}),
            data=data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Premium 80-Page Exercise Book (Edited)')
        self.assertEqual(self.product.retail_price, Decimal('4.20'))
        self.assertEqual(self.product.wholesale_price, Decimal('400.00'))
        self.assertEqual(self.product.stock_status, 'AVAILABLE_ON_ORDER')
        self.assertTrue(self.product.is_customizable)

    def test_product_delete(self):
        """Deleting a product."""
        pk = self.product.pk
        response = self.client.post(
            reverse('catalog:product_delete', kwargs={'pk': pk}),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Product.objects.filter(pk=pk).exists())

    def test_category_create(self):
        """Creating a new product category."""
        response = self.client.post(
            reverse('catalog:category_create'),
            data={'name': 'Mathematical Sets', 'icon_class': 'fas fa-compass'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Category.objects.filter(name='Mathematical Sets').exists())
