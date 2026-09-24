from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from managerial.models import SchoolCreditRecord, RegionalWaybill
from orders.models import POSSale
from customizer.models import CustomBookOrder
from invoices.models import Invoice


class ManagerialCRUDTestCase(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='executive_ceo',
            password='testpassword123',
            is_staff=True,
            is_superuser=True
        )
        self.client = Client()
        self.client.login(username='executive_ceo', password='testpassword123')

        self.credit = SchoolCreditRecord.objects.create(
            school_name='Notre Dame Girls Senior High',
            location='Fiapre - Sunyani',
            principal_name='Sr. Mary',
            phone_number='024 111 2233',
            academic_term='Term 1 (2026/2027)',
            total_credit_granted=Decimal('15000.00'),
            amount_paid=Decimal('5000.00'),
            term_due_date=timezone.now().date() + timedelta(days=30),
            notes='Initial supply agreement'
        )

        self.waybill = RegionalWaybill.objects.create(
            waybill_number='VIP-SNY-9901',
            carrier='VIP_JEOUN',
            origin_hub='Sunyani Main Hub',
            destination_town='Kumasi (Asafo)',
            recipient_name='Opoku Ware School Bookstore',
            recipient_phone='024 333 4444',
            consignment_summary='20 Cartons of Exercise Books',
            status='IN_TRANSIT'
        )

    def test_dashboard_view_dynamic_stats(self):
        """Dashboard renders with dynamically computed stats from database."""
        response = self.client.get(reverse('managerial:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Operations Dashboard')
        # Check presence of dynamic context
        self.assertIn('stats', response.context)
        self.assertIn('today_sales', response.context['stats'])
        self.assertIn('monthly_revenue', response.context['stats'])
        self.assertIn('recent_orders', response.context)

    def test_credit_ledger_view(self):
        """Staff can view credit ledger."""
        response = self.client.get(reverse('managerial:credit_ledger'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Notre Dame Girls Senior High')
        self.assertContains(response, '10,000.00') # 15000 - 5000 balance

    def test_create_credit_record(self):
        """Staff can register a new school credit account."""
        data = {
            'school_name': 'Sunyani Senior High Technical',
            'location': 'Sunyani South',
            'principal_name': 'Mr. Mensah',
            'phone_number': '024 555 6789',
            'academic_term': 'Term 1 (2026/2027)',
            'total_credit_granted': '12000.00',
            'term_due_date': (timezone.now().date() + timedelta(days=60)).strftime('%Y-%m-%d'),
            'notes': 'Government approved credit supply.',
        }
        response = self.client.post(reverse('managerial:create_credit_record'), data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        record = SchoolCreditRecord.objects.get(school_name='Sunyani Senior High Technical')
        self.assertEqual(record.total_credit_granted, Decimal('12000.00'))
        self.assertEqual(record.balance_outstanding, Decimal('12000.00'))
        self.assertEqual(record.status, 'CURRENT')

    def test_edit_credit_record(self):
        """Staff can edit credit terms and record payments."""
        data = {
            'school_name': 'Notre Dame Girls Senior High (Updated)',
            'location': 'Fiapre - Sunyani West',
            'principal_name': 'Sr. Mary Concepta',
            'phone_number': '024 111 2233',
            'total_credit_granted': '15000.00',
            'amount_paid': '10000.00',
            'term_due_date': (timezone.now().date() + timedelta(days=15)).strftime('%Y-%m-%d'),
            'notes': 'Recorded second installment of GH₵ 5,000.',
        }
        response = self.client.post(
            reverse('managerial:edit_credit_record', kwargs={'pk': self.credit.pk}),
            data=data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        self.credit.refresh_from_db()
        self.assertEqual(self.credit.school_name, 'Notre Dame Girls Senior High (Updated)')
        self.assertEqual(self.credit.amount_paid, Decimal('10000.00'))
        self.assertEqual(self.credit.balance_outstanding, Decimal('5000.00'))
        self.assertEqual(self.credit.status, 'PARTIALLY_PAID')

    def test_delete_credit_record(self):
        """CEO can delete a credit record."""
        pk = self.credit.pk
        response = self.client.post(
            reverse('managerial:delete_credit_record', kwargs={'pk': pk}),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SchoolCreditRecord.objects.filter(pk=pk).exists())

    def test_update_waybill_status(self):
        """Logistics officer can update waybill delivery progress."""
        data = {
            'status': 'DELIVERED_AND_SIGNED',
            'driver_conductor_name': 'Driver Kojo Appiah',
            'driver_phone': '024 777 8899',
        }
        response = self.client.post(
            reverse('managerial:update_waybill_status', kwargs={'pk': self.waybill.pk}),
            data=data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        self.waybill.refresh_from_db()
        self.assertEqual(self.waybill.status, 'DELIVERED_AND_SIGNED')
        self.assertEqual(self.waybill.driver_conductor_name, 'Driver Kojo Appiah')
        self.assertIsNotNone(self.waybill.delivered_at)

    def test_delete_waybill(self):
        """Logistics manager can delete a completed or void waybill."""
        pk = self.waybill.pk
        response = self.client.post(
            reverse('managerial:delete_waybill', kwargs={'pk': pk}),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(RegionalWaybill.objects.filter(pk=pk).exists())
