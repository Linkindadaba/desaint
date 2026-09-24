from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from invoices.models import Invoice, InvoiceItem


class InvoicesCRUDTestCase(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='bursar_staff',
            password='testpassword123',
            is_staff=True,
            is_superuser=True
        )
        self.client = Client()
        self.client.login(username='bursar_staff', password='testpassword123')

        self.invoice = Invoice.objects.create(
            invoice_number='PRO-2026-NDS-TEST01',
            invoice_type='INSTITUTIONAL_PROFORMA',
            tax_mode='INSTITUTIONAL_WHT_3PCT',
            client_name='Sunyani Senior High School',
            client_phone='024 123 4567',
            client_tin='P0099887766',
            subtotal=Decimal('10000.00'),
            vat_amount=Decimal('0.00'),
            wht_amount=Decimal('300.00'),
            total_payable=Decimal('9700.00'),
            payment_method='BANK_TRANSFER',
            notes='Supply of customized exercise books for Term 1.'
        )
        InvoiceItem.objects.create(
            invoice=self.invoice,
            description='Custom Exercise Books 80pg Single Line',
            quantity=2500,
            unit_price=Decimal('4.00'),
            total_price=Decimal('10000.00')
        )

    def test_invoice_list_view(self):
        """Staff can view invoices ledger with summary stats."""
        response = self.client.get(reverse('invoices:invoice_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sunyani Senior High School')
        self.assertContains(response, 'PRO-2026-NDS-TEST01')
        self.assertContains(response, '9,700.00')

    def test_invoice_create_institutional_wht(self):
        """Creates institutional proforma with statutory Act 896 3% WHT calculation."""
        data = {
            'client_name': 'Twene Amanfo Senior High Technical',
            'client_phone': '020 987 6543',
            'client_tin': 'P0011223344',
            'invoice_type': 'INSTITUTIONAL_PROFORMA',
            'tax_mode': 'INSTITUTIONAL_WHT_3PCT',
            'payment_method': 'BANK_TRANSFER',
            'item_description[]': ['Custom Exam Answer Booklets', 'Office Whiteboard Markers'],
            'item_quantity[]': ['2000', '100'],
            'item_unit_price[]': ['5.00', '10.00'],
            'notes': 'Government procurement contract.',
        }
        # 2000 * 5.00 = 10000.00
        # 100 * 10.00 = 1000.00
        # Subtotal = 11000.00
        # 3% WHT = 330.00
        # Net Payable = 10670.00
        response = self.client.post(reverse('invoices:invoice_create'), data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        inv = Invoice.objects.get(client_name='Twene Amanfo Senior High Technical')
        self.assertEqual(inv.subtotal, Decimal('11000.00'))
        self.assertEqual(inv.wht_amount, Decimal('330.00'))
        self.assertEqual(inv.vat_amount, Decimal('0.00'))
        self.assertEqual(inv.total_payable, Decimal('10670.00'))
        self.assertEqual(inv.items.count(), 2)

    def test_invoice_create_standard_vat(self):
        """Creates standard commercial invoice with 21% GRA VAT."""
        data = {
            'client_name': 'Bono Regional Educational Supplies Ltd',
            'client_phone': '055 333 4444',
            'invoice_type': 'WHOLESALE_INVOICE',
            'tax_mode': 'GRA_STANDARD_VAT',
            'payment_method': 'MOMO_TILL',
            'item_description[]': ['A4 Copy Paper Cartons'],
            'item_quantity[]': ['10'],
            'item_unit_price[]': ['200.00'],
        }
        # 10 * 200 = 2000.00
        # VAT 21% = 420.00
        # Total Payable = 2420.00
        response = self.client.post(reverse('invoices:invoice_create'), data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        inv = Invoice.objects.get(client_name='Bono Regional Educational Supplies Ltd')
        self.assertEqual(inv.subtotal, Decimal('2000.00'))
        self.assertEqual(inv.vat_amount, Decimal('420.00'))
        self.assertEqual(inv.total_payable, Decimal('2420.00'))

    def test_invoice_mark_paid(self):
        """Records payment transaction reference."""
        self.assertFalse(self.invoice.is_paid)
        response = self.client.post(
            reverse('invoices:mark_paid', kwargs={'pk': self.invoice.pk}),
            data={'payment_reference': 'GCB-TRX-2026-9901'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.invoice.refresh_from_db()
        self.assertTrue(self.invoice.is_paid)
        self.assertEqual(self.invoice.payment_reference, 'GCB-TRX-2026-9901')

    def test_invoice_delete(self):
        """CEO can delete an invoice."""
        pk = self.invoice.pk
        response = self.client.post(
            reverse('invoices:delete', kwargs={'pk': pk}),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Invoice.objects.filter(pk=pk).exists())

    def test_invoice_proforma_printable_view(self):
        """Printable A4 proforma invoice renders properly with items."""
        response = self.client.get(reverse('invoices:proforma', kwargs={'pk': self.invoice.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sunyani Senior High School')
        self.assertContains(response, 'PRO-2026-NDS-TEST01')
        self.assertContains(response, 'Custom Exercise Books 80pg Single Line')
