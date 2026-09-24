import os
import django
from decimal import Decimal
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Category, Product
from customizer.models import RulingOption, CustomBookOrder
from managerial.models import SchoolCreditRecord, RegionalWaybill
from invoices.models import Invoice, InvoiceItem
from orders.models import POSSale

def seed_data():
    print("Seeding initial data for Desaint Stationeries...")

    # 1. Categories
    cat_books, _ = Category.objects.get_or_create(
        name="Exercise & Note Books",
        slug="exercise-note-books",
        defaults={'icon_class': 'fas fa-book', 'display_order': 1}
    )
    cat_paper, _ = Category.objects.get_or_create(
        name="Paper Supplies & Reams",
        slug="paper-supplies-reams",
        defaults={'icon_class': 'fas fa-file-lines', 'display_order': 2}
    )
    cat_pens, _ = Category.objects.get_or_create(
        name="Writing & Drawing Instruments",
        slug="writing-drawing-instruments",
        defaults={'icon_class': 'fas fa-pen', 'display_order': 3}
    )
    cat_sets, _ = Category.objects.get_or_create(
        name="Mathematical & Classroom Tools",
        slug="mathematical-classroom-tools",
        defaults={'icon_class': 'fas fa-ruler-combined', 'display_order': 4}
    )

    # 2. Products
    products_data = [
        {
            'name': 'Desaint Standard Exercise Book (80 Pages)',
            'slug': 'desaint-standard-exercise-book-80pg',
            'category': cat_books,
            'sku': 'DSP-EX-80',
            'description': 'Premium 70gsm bright white bond paper with 250gsm gloss laminated cover.',
            'retail_price': Decimal('4.50'),
            'wholesale_price': Decimal('3.20'),
            'wholesale_box_size': 'Box of 120 Books',
            'stock_status': 'IN_STOCK',
            'stock_quantity': 4500,
            'icon_class': 'fas fa-book text-primary',
            'image': 'products/exercise_80pg.jpg',
            'is_customizable': True
        },
        {
            'name': 'Hardcover Note 1 Notebook (160 Pages)',
            'slug': 'hardcover-note-1-notebook-160pg',
            'category': cat_books,
            'sku': 'DSP-NT-160',
            'description': 'Section sewn durable hardcover notebook for JHS, SHS, and colleges.',
            'retail_price': Decimal('12.00'),
            'wholesale_price': Decimal('9.50'),
            'wholesale_box_size': 'Carton of 48 Books',
            'stock_status': 'IN_STOCK',
            'stock_quantity': 1800,
            'icon_class': 'fas fa-book-bookmark text-success',
            'image': 'products/hardcover_160pg.jpg',
            'is_customizable': True
        },
        {
            'name': 'Pre-School Grid & Tracing Activity Book',
            'slug': 'pre-school-grid-tracing-activity-book',
            'category': cat_books,
            'sku': 'DSP-KG-GRID',
            'description': 'Kindergarten handwriting guide with standard double-line and counting grids.',
            'retail_price': Decimal('6.00'),
            'wholesale_price': Decimal('4.80'),
            'wholesale_box_size': 'Pack of 50 Books',
            'stock_status': 'AVAILABLE_ON_ORDER',
            'stock_quantity': 600,
            'icon_class': 'fas fa-pencil text-warning',
            'image': 'products/preschool_grid.jpg',
            'is_customizable': True
        },
        {
            'name': 'A4 Copy Paper Bond 80gsm (Box of 5 Reams)',
            'slug': 'a4-copy-paper-bond-80gsm-box-5-reams',
            'category': cat_paper,
            'sku': 'DSP-PPR-A4',
            'description': 'High-opacity, jam-free imported 80gsm A4 sheets for high-speed copiers and school exams.',
            'retail_price': Decimal('240.00'),
            'wholesale_price': Decimal('215.00'),
            'wholesale_box_size': 'Box of 5 Reams (2,500 Sheets)',
            'stock_status': 'IN_STOCK',
            'stock_quantity': 420,
            'icon_class': 'fas fa-file-lines text-info',
            'image': 'products/a4_copy_paper.jpg',
            'is_customizable': False
        },
        {
            'name': 'Permanent High-Yield Marker Pen (Box of 12)',
            'slug': 'permanent-high-yield-marker-pen-box-12',
            'category': cat_pens,
            'sku': 'DSP-MRK-12',
            'description': 'Chisel tip waterproof markers for whiteboards, school signage, and cartons.',
            'retail_price': Decimal('45.00'),
            'wholesale_price': Decimal('36.00'),
            'wholesale_box_size': 'Carton of 24 Boxes',
            'stock_status': 'IN_STOCK',
            'stock_quantity': 350,
            'icon_class': 'fas fa-pen text-dark',
            'image': 'products/marker_pens.jpg',
            'is_customizable': False
        },
        {
            'name': 'Mathematical Geometry & Instrument Set',
            'slug': 'mathematical-geometry-instrument-set',
            'category': cat_sets,
            'sku': 'DSP-MTH-SET',
            'description': 'Durable metal tin containing compass, divider, 15cm ruler, protractor, and set squares.',
            'retail_price': Decimal('15.00'),
            'wholesale_price': Decimal('11.50'),
            'wholesale_box_size': 'Carton of 60 Sets',
            'stock_status': 'IN_STOCK',
            'stock_quantity': 750,
            'icon_class': 'fas fa-ruler-combined text-warning',
            'image': 'products/geometry_set.jpg',
            'is_customizable': False
        }
    ]

    for p in products_data:
        Product.objects.get_or_create(sku=p['sku'], defaults=p)

    # 3. Ruling Options
    rulings_data = [
        {'name': 'Standard Exercise (80 Pages - Single Line)', 'category': 'EXERCISE', 'page_count': 80, 'base_unit_price': Decimal('3.20'), 'is_popular': True},
        {'name': 'Standard Exercise (60 Pages - Single Line)', 'category': 'EXERCISE', 'page_count': 60, 'base_unit_price': Decimal('2.80'), 'is_popular': False},
        {'name': 'Standard Exercise (40 Pages - Single Line)', 'category': 'EXERCISE', 'page_count': 40, 'base_unit_price': Decimal('2.50'), 'is_popular': False},
        {'name': 'Hardcover Note 1 Notebook (160 Pages)', 'category': 'NOTE', 'page_count': 160, 'base_unit_price': Decimal('9.50'), 'is_popular': True},
        {'name': 'Hardcover Note 3 Notebook (200 Pages)', 'category': 'NOTE', 'page_count': 200, 'base_unit_price': Decimal('12.00'), 'is_popular': False},
        {'name': 'Pre-School Grid & Counting Activity Book', 'category': 'KINDERGARTEN', 'page_count': 60, 'base_unit_price': Decimal('4.20'), 'is_popular': True},
        {'name': 'Pre-School Double-Line Handwriting Book', 'category': 'KINDERGARTEN', 'page_count': 60, 'base_unit_price': Decimal('4.20'), 'is_popular': False},
    ]

    ruling_objs = {}
    for r in rulings_data:
        obj, _ = RulingOption.objects.get_or_create(name=r['name'], defaults=r)
        ruling_objs[r['name']] = obj

    # 4. Custom Book Orders
    ex80 = ruling_objs.get('Standard Exercise (80 Pages - Single Line)')
    if ex80 and not CustomBookOrder.objects.filter(order_ref='DSP-2026-STJ-0042').exists():
        CustomBookOrder.objects.create(
            order_ref='DSP-2026-STJ-0042',
            school_name='St. James Seminary Senior High School',
            proprietor_name='Rev. Fr. Emmanuel Mensah',
            contact_phone='024 400 1122',
            contact_email='info@stjamesseminary.edu.gh',
            delivery_location='St. James Campus, Sunyani',
            ruling=ex80,
            quantity=7500,
            status='PROOF_APPROVED',
            digital_proof_approved=True,
            approved_by_signatory='Rev. Fr. Emmanuel Mensah',
            notes='Front cover full crest gloss laminated; back cover school anthem and rules.'
        )

    # 5. School Credit Records
    credits_data = [
        {
            'school_name': 'Ridge Experimental Basic School',
            'location': 'Sunyani',
            'principal_name': 'Mr. K. Owusu (Headmaster)',
            'phone_number': '024 311 8899',
            'total_credit_granted': Decimal('28500.00'),
            'amount_paid': Decimal('15000.00'),
            'term_due_date': date.today() + timedelta(days=35),
            'status': 'PARTIALLY_PAID',
        },
        {
            'school_name': 'Sacred Heart Senior High School',
            'location': 'Nsoatre',
            'principal_name': 'Sister Faustina (Bursar)',
            'phone_number': '020 902 4433',
            'total_credit_granted': Decimal('16200.00'),
            'amount_paid': Decimal('11300.00'),
            'term_due_date': date.today() + timedelta(days=50),
            'status': 'PARTIALLY_PAID',
        },
        {
            'school_name': 'Sunyani Model Islamic Basic',
            'location': 'Sunyani',
            'principal_name': 'Alhaji Moro (Proprietor)',
            'phone_number': '024 455 6789',
            'total_credit_granted': Decimal('9600.00'),
            'amount_paid': Decimal('9600.00'),
            'term_due_date': date.today() - timedelta(days=5),
            'status': 'FULLY_SETTLED',
        },
        {
            'school_name': 'Dormaa Community Basic School',
            'location': 'Dormaa Ahenkro',
            'principal_name': 'Madam Grace Boateng',
            'phone_number': '024 788 3311',
            'total_credit_granted': Decimal('12400.00'),
            'amount_paid': Decimal('0.00'),
            'term_due_date': date.today() + timedelta(days=15),
            'status': 'OVERDUE_NOTICE',
        }
    ]

    for c in credits_data:
        SchoolCreditRecord.objects.get_or_create(school_name=c['school_name'], defaults=c)

    # 6. Regional Bus Waybills
    waybills_data = [
        {
            'waybill_number': 'VIP-SNY-8841',
            'carrier': 'VIP_JEOUN',
            'origin_hub': 'Sunyani Main Hub',
            'destination_town': 'Kumasi (Asafo)',
            'recipient_name': 'Agyeiwaa Bookshop & Stationery',
            'recipient_phone': '024 332 9901',
            'consignment_summary': '6 Heavy Cartons (Copy Paper & Exercise Books)',
            'driver_conductor_name': 'Driver Kwabena',
            'driver_phone': '024 112 3344',
            'status': 'IN_TRANSIT',
        },
        {
            'waybill_number': 'OA-SNY-2190',
            'carrier': 'OA_TRAVEL',
            'origin_hub': 'Sunyani Main Hub',
            'destination_town': 'Tamale (Central Station)',
            'recipient_name': 'Northern Educational Supplies',
            'recipient_phone': '020 887 6655',
            'consignment_summary': '12 Parcels (Custom School Exercise Books)',
            'driver_conductor_name': 'Driver Haruna',
            'driver_phone': '027 990 1122',
            'status': 'ARRIVED_AT_TERMINAL',
        },
        {
            'waybill_number': 'IMP-SNY-0455',
            'carrier': 'IMPERIAL_EXPRESS',
            'origin_hub': 'Sunyani Main Hub',
            'destination_town': 'Takoradi (Market Circle)',
            'recipient_name': 'Western Star Academy',
            'recipient_phone': '024 554 1122',
            'consignment_summary': '8 Cartons (Hardcover Note 1 Books)',
            'driver_conductor_name': 'Driver Mensah',
            'driver_phone': '024 667 8899',
            'status': 'DELIVERED_AND_SIGNED',
        },
    ]

    for w in waybills_data:
        RegionalWaybill.objects.get_or_create(waybill_number=w['waybill_number'], defaults=w)

    print("Initial data seeded successfully!")

if __name__ == '__main__':
    seed_data()
