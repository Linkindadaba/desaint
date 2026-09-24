from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse

from catalog.models import Category, Product


class CoreStorefrontTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Exercise Books', slug='exercise-books')
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

    def test_homepage_renders(self):
        """Storefront homepage renders with products, categories, and corporate trust strip."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Standard 80-Page Exercise Book')
        self.assertContains(response, 'Exercise Books')
        self.assertContains(response, 'Direct Factory School Printing')

    def test_about_page(self):
        """About page renders company story and executive leadership."""
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'About')

    def test_citations_page(self):
        """Citations and institutional trust page renders official certifications."""
        response = self.client.get(reverse('core:citations'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Citations')

    def test_contact_page_get_and_post(self):
        """Contact page renders form and processes customer inquiries."""
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)

        data = {
            'name': 'Proprietor Kwadwo Asare',
            'phone': '024 888 9900',
            'institution': 'Sunyani Model Academy',
            'message': 'Inquiry regarding 8,000 customized exercise books for Term 1.',
        }
        post_resp = self.client.post(reverse('core:contact'), data=data, follow=True)
        self.assertEqual(post_resp.status_code, 200)
        self.assertContains(post_resp, 'Thank you, Proprietor Kwadwo Asare')
