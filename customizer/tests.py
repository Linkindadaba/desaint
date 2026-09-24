from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from customizer.models import RulingOption, CustomBookOrder


class CustomizerEngineTestCase(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='graphics_lead',
            password='testpassword123',
            is_staff=True,
            is_superuser=True
        )
        self.client = Client()
        self.client.login(username='graphics_lead', password='testpassword123')

        self.ruling = RulingOption.objects.create(
            name='80-Page Single Line Ruling',
            category='EXERCISE',
            page_count=80,
            base_unit_price=Decimal('3.20'),
            is_popular=True,
            is_active=True
        )

        self.order = CustomBookOrder.objects.create(
            order_ref='DSP-2026-STJ-001',
            school_name='St. James Seminary Senior High',
            proprietor_name='Very Rev. Fr. Principal',
            contact_phone='024 400 1122',
            delivery_location='Sunyani Campus',
            ruling=self.ruling,
            quantity=5000,
            status='PROOF_PENDING'
        )

    def test_configurator_view_dual_access_storefront(self):
        """Anonymous public visitor accesses configurator using base_storefront.html (Rule 7)."""
        anon_client = Client()
        response = anon_client.get(reverse('customizer:configurator'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['base_template'], 'base_storefront.html')
        self.assertContains(response, '80-Page Single Line Ruling')

    def test_configurator_view_dual_access_staff(self):
        """Authenticated staff accesses configurator using base_admin.html (Rule 7)."""
        response = self.client.get(reverse('customizer:configurator'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['base_template'], 'base_admin.html')

    def test_customizer_submit_and_financials(self):
        """Submitting a 5,000-copy run calculates Act 896 3% WHT and free plate setup."""
        data = {
            'school_name': 'Notre Dame Girls Senior High',
            'proprietor_name': 'Sr. Headmistress',
            'contact_phone': '020 111 2233',
            'contact_email': 'info@notredame.edu.gh',
            'delivery_location': 'Fiapre - Sunyani',
            'ruling_id': self.ruling.id,
            'quantity': '6000',
            'school_motto': 'Truth and Virtue',
            'back_cover_content': 'School Anthem and National Pledge',
        }
        response = self.client.post(reverse('customizer:submit'), data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        order = CustomBookOrder.objects.get(school_name='Notre Dame Girls Senior High')
        # 6000 * 3.20 = 19200.00
        self.assertEqual(order.gross_amount, Decimal('19200.00'))
        # 3% WHT = 576.00
        self.assertEqual(order.wht_deducted, Decimal('576.00'))
        # Net Payable = 18624.00
        self.assertEqual(order.net_payable, Decimal('18624.00'))
        self.assertEqual(order.plate_setup_fee, Decimal('0.00'))
        self.assertEqual(order.status, 'PROOF_PENDING')

    def test_proof_detail_view(self):
        """Digital proof approval page displays vector simulation and specifications."""
        response = self.client.get(reverse('customizer:proof_detail', kwargs={'pk': self.order.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'St. James Seminary Senior High')
        self.assertContains(response, 'DSP-2026-STJ-001')

    def test_proof_signoff(self):
        """Proprietor or staff signs off digital proof, logging timestamp and signatory."""
        self.assertFalse(self.order.digital_proof_approved)
        data = {'signatory_name': 'Rev. Fr. Principal Owusu'}
        response = self.client.post(
            reverse('customizer:proof_detail', kwargs={'pk': self.order.pk}),
            data=data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()
        self.assertTrue(self.order.digital_proof_approved)
        self.assertEqual(self.order.status, 'PROOF_APPROVED')
        self.assertEqual(self.order.approved_by_signatory, 'Rev. Fr. Principal Owusu')
        self.assertIsNotNone(self.order.approval_timestamp)

    def test_order_list_view(self):
        """Staff can view directory of school custom print orders."""
        response = self.client.get(reverse('customizer:order_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'St. James Seminary Senior High')
        self.assertContains(response, 'DSP-2026-STJ-001')

    def test_order_status_update(self):
        """Staff can progress order through press manufacturing stages."""
        data = {
            'status': 'PRINTING',
            'notes': 'Printing on Heidelberg 4-color offset press.'
        }
        response = self.client.post(
            reverse('customizer:order_status_update', kwargs={'pk': self.order.pk}),
            data=data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'PRINTING')
        self.assertIn('Heidelberg', self.order.notes)

    def test_order_delete(self):
        """CEO can remove a custom order."""
        pk = self.order.pk
        response = self.client.post(
            reverse('customizer:order_delete', kwargs={'pk': pk}),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CustomBookOrder.objects.filter(pk=pk).exists())
