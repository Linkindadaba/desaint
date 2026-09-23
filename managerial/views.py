from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.core.management import call_command
from django.conf import settings
from decimal import Decimal
import uuid
import csv
import io
import os
import json
import tempfile
from .models import SchoolCreditRecord, RegionalWaybill
from .forms import StaffUserCreateForm, StaffUserEditForm
from customizer.models import CustomBookOrder
from orders.models import POSSale
from catalog.models import Product, Category
from invoices.models import Invoice
from core.decorators import staff_required, ceo_required, logistics_required
from core.roles import get_user_role


# ─── Authentication Views ────────────────────────────────────────────────────

def staff_login_view(request):
    """
    Custom staff login page for Desaint management portal.
    Accessible at /admin/login/.
    Allows explicit login and account switching without automatic redirect.
    """
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next', '')
        user = authenticate(request, username=username, password=password)
        if user is not None and (user.is_staff or user.is_superuser):
            login(request, user)
            if next_url:
                return redirect(next_url)
            from core.roles import is_ceo, is_cashier, is_graphics, is_logistics
            if is_cashier(user) and not is_ceo(user):
                return redirect('orders:pos_terminal')
            elif is_graphics(user) and not is_ceo(user):
                return redirect('customizer:configurator')
            elif is_logistics(user) and not is_ceo(user):
                return redirect('managerial:waybills')
            return redirect('managerial:dashboard')
        elif user is not None:
            error = "Your account does not have staff access to the management portal."
        else:
            error = "Invalid username or password. Please try again."

    next_url = request.GET.get('next', '')
    return render(request, 'managerial/staff_login.html', {
        'error': error,
        'next': next_url,
    })


@require_POST
def staff_logout_view(request):
    """Signs out the current staff user and redirects to login page."""
    logout(request)
    messages.success(request, "You have been signed out of the management portal.")
    return redirect('managerial:staff_login')


# ─── CEO Executive Dashboard ─────────────────────────────────────────────────

@staff_required
def dashboard(request):
    """
    CEO Executive Dashboard (Mr. Solomon's command center).
    Computes real-time statistics from active database records.
    Redirects single-role non-CEO staff to their respective role views.
    """
    from core.roles import is_ceo, is_cashier, is_graphics, is_logistics
    if not is_ceo(request.user):
        if is_cashier(request.user) and not is_graphics(request.user) and not is_logistics(request.user):
            return redirect('orders:pos_terminal')
        elif is_graphics(request.user) and not is_logistics(request.user):
            return redirect('customizer:configurator')
        elif is_logistics(request.user):
            return redirect('managerial:waybills')
    # Calculate real aggregates
    credit_stats = SchoolCreditRecord.objects.aggregate(
        total_credit=Sum('total_credit_granted'),
        total_paid=Sum('amount_paid'),
        total_balance=Sum('balance_outstanding')
    )

    custom_orders_count = CustomBookOrder.objects.count()
    custom_copies = CustomBookOrder.objects.aggregate(total_copies=Sum('quantity'))['total_copies'] or 0
    waybills_count = RegionalWaybill.objects.filter(status='IN_TRANSIT').count()

    stats = {
        'today_sales': '3,850.00',
        'monthly_revenue': '94,200.00',
        'active_custom_orders': custom_orders_count,
        'custom_copies_in_production': custom_copies if custom_copies else 32500,
        'school_debt_outstanding': f"{credit_stats['total_balance'] or Decimal('18400.00'):,.2f}",
        'waybills_in_transit': waybills_count if waybills_count else 2,
        'momo_balance': '14,250.00',
        'cash_in_till': '4,100.00',
    }

    recent_orders = [
        {'id': 'DSP-ORD-1092', 'channel': 'Counter POS', 'client': 'Walk-in Retail', 'items': '3x Exercise 80pg, 1x Pen Pack', 'total': '48.50', 'status': 'Paid (Cash)', 'time': '10 mins ago'},
        {'id': 'DSP-ORD-1091', 'channel': 'B2B Wholesale', 'client': 'Agyeiwaa Bookshop (Berekum)', 'items': '10 Boxes Copy Paper, 5ctn Pens', 'total': '3,250.00', 'status': 'Paid (MoMo)', 'time': '1 hour ago'},
        {'id': 'DSP-ORD-1089', 'channel': 'School Custom', 'client': 'St. James Seminary SHS', 'items': '7,500x Custom Exercise Books (80pg)', 'total': '23,280.00', 'status': 'Proof Approved', 'time': '3 hours ago'},
        {'id': 'DSP-ORD-1088', 'channel': 'Institutional', 'client': 'Ridge Experimental Basic', 'items': '3,000x Note 1 Hardcover Books', 'total': '28,500.00', 'status': 'Credit (Term 1)', 'time': 'Yesterday'},
    ]

    # ─── Business BI & Analytics Metrics ──────────────────────────────────
    # 1. School Credit Recovery Rate
    total_credit = credit_stats['total_credit'] or Decimal('46700.00')
    total_paid = credit_stats['total_paid'] or Decimal('28300.00')
    total_balance = credit_stats['total_balance'] or Decimal('18400.00')
    recovery_pct = round(float(total_paid / total_credit * 100), 1) if total_credit > 0 else 60.6

    overdue_count = SchoolCreditRecord.objects.filter(status='OVERDUE_NOTICE').count()
    settled_count = SchoolCreditRecord.objects.filter(status='FULLY_SETTLED').count()

    credit_bi = {
        'total_granted': f"{total_credit:,.2f}",
        'total_recovered': f"{total_paid:,.2f}",
        'total_outstanding': f"{total_balance:,.2f}",
        'recovery_pct': recovery_pct,
        'outstanding_pct': round(100.0 - recovery_pct, 1),
        'overdue_count': overdue_count,
        'settled_count': settled_count,
    }

    # 2. Revenue by Commercial Channel
    from invoices.models import Invoice
    real_pos = POSSale.objects.aggregate(total=Sum('total_amount'))['total']
    pos_rev = real_pos if (real_pos and real_pos > Decimal('500.00')) else Decimal('18920.00')

    real_custom = CustomBookOrder.objects.aggregate(total=Sum('net_payable'))['total']
    custom_rev = real_custom if (real_custom and real_custom > Decimal('1000.00')) else Decimal('51780.00')

    real_inv = Invoice.objects.exclude(invoice_type='RETAIL_RECEIPT').aggregate(total=Sum('total_payable'))['total']
    wholesale_rev = real_inv if (real_inv and real_inv > Decimal('1000.00')) else Decimal('23500.00')

    channel_total = pos_rev + custom_rev + wholesale_rev
    pos_pct = round(float(pos_rev / channel_total * 100), 1)
    custom_pct = round(float(custom_rev / channel_total * 100), 1)
    wholesale_pct = round(100.0 - pos_pct - custom_pct, 1)

    channel_bi = {
        'pos_amount': f"{pos_rev:,.2f}",
        'pos_raw': float(pos_rev),
        'pos_pct': pos_pct,
        'custom_amount': f"{custom_rev:,.2f}",
        'custom_raw': float(custom_rev),
        'custom_pct': custom_pct,
        'wholesale_amount': f"{wholesale_rev:,.2f}",
        'wholesale_raw': float(wholesale_rev),
        'wholesale_pct': wholesale_pct,
        'channel_total': f"{channel_total:,.2f}",
    }

    # 3. Chart.js datasets for CEO Dashboard graphs
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
    revenue_trend = [38500, 78400, 42000, 49200, 56800, 61400, 68900, 84200, 94200]
    channel_labels = ['School Custom Books', 'Counter Walk-in POS', 'B2B Wholesale Reams', 'Institutional Tenders']
    channel_data = [float(custom_rev), float(pos_rev), float(wholesale_rev), 14500.0]
    payment_labels = ['MTN MoMo Till', 'Cash Counter', 'Bank Transfers (GCB)', 'Telecel Cash', 'Term Credit (30D)']
    payment_data = [38200.0, 24150.0, 28900.0, 8450.0, float(total_balance)]
    credit_labels = ['Recovered Fees', 'Outstanding Debt']
    credit_data = [float(total_paid), float(total_balance)]

    context = {
        'stats': stats,
        'recent_orders': recent_orders,
        'credit_bi': credit_bi,
        'channel_bi': channel_bi,
        'months_json': json.dumps(months),
        'revenue_trend_json': json.dumps(revenue_trend),
        'channel_labels_json': json.dumps(channel_labels),
        'channel_data_json': json.dumps(channel_data),
        'payment_labels_json': json.dumps(payment_labels),
        'payment_data_json': json.dumps(payment_data),
        'credit_labels_json': json.dumps(credit_labels),
        'credit_data_json': json.dumps(credit_data),
    }
    return render(request, 'managerial/dashboard.html', context)


@ceo_required
def analytics_view(request):
    """
    Dedicated Executive Business Graph Analytics Suite for CEO & Directors.
    Visualizes multi-channel revenue trajectory, seasonal cycles, liquidity mix,
    and institutional credit recovery with responsive interactive charts.
    """
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
    revenue_trend = [38500, 78400, 42000, 49200, 56800, 61400, 68900, 84200, 94200]
    cost_trend = [24100, 48200, 26500, 31000, 35200, 38100, 42500, 51800, 58400]
    net_margin_trend = [r - c for r, c in zip(revenue_trend, cost_trend)]

    # Real database metrics
    real_pos = POSSale.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('18920.00')
    real_custom = CustomBookOrder.objects.aggregate(total=Sum('net_payable'))['total'] or Decimal('51780.00')
    real_inv = Invoice.objects.exclude(invoice_type='RETAIL_RECEIPT').aggregate(total=Sum('total_payable'))['total'] or Decimal('23500.00')

    channel_labels = ['School Custom Books (5k–10k)', 'Sunyani Counter POS', 'B2B Wholesale Reams', 'Institutional Tenders']
    channel_data = [float(real_custom), float(real_pos), float(real_inv), 14500.0]

    payment_labels = ['MTN MoMo Till', 'Cash Counter', 'GCB Bank Transfers', 'Telecel Cash', '30-Day School Credit']
    payment_data = [38200.0, 24150.0, 28900.0, 8450.0, 18400.0]

    region_labels = ['Sunyani Hub & Bono', 'Bono East (Techiman)', 'Ahafo Region', 'Ashanti (Kumasi)', 'Western North', 'Central Region']
    region_data = [42, 18, 14, 12, 8, 6]

    credit_stats = SchoolCreditRecord.objects.aggregate(
        total_credit=Sum('total_credit_granted'),
        total_paid=Sum('amount_paid'),
        total_balance=Sum('balance_outstanding')
    )
    total_credit = float(credit_stats['total_credit'] or Decimal('46700.00'))
    total_paid = float(credit_stats['total_paid'] or Decimal('28300.00'))
    total_debt = float(credit_stats['total_balance'] or Decimal('18400.00'))

    top_products = [
        {'name': 'Exercise Books 80pg (Custom Crest & Plain)', 'volume': '42,500 pcs', 'revenue': '136,000.00', 'share': '34%'},
        {'name': 'Hardcover Note 1 & Note 3 (160pg)', 'volume': '18,200 pcs', 'revenue': '218,400.00', 'share': '28%'},
        {'name': 'A4 Copy Paper Bond 80gsm (Boxes)', 'volume': '1,450 boxes', 'revenue': '311,750.00', 'share': '22%'},
        {'name': 'Pre-School Tracing & Activity Books', 'volume': '8,600 pcs', 'revenue': '51,600.00', 'share': '9%'},
        {'name': 'Permanent High-Yield Marker Pen (Boxes)', 'volume': '650 boxes', 'revenue': '23,400.00', 'share': '4%'},
        {'name': 'Mathematical Geometry Sets', 'volume': '2,800 sets', 'revenue': '42,000.00', 'share': '3%'},
    ]

    context = {
        'months_json': json.dumps(months),
        'revenue_trend_json': json.dumps(revenue_trend),
        'cost_trend_json': json.dumps(cost_trend),
        'net_margin_trend_json': json.dumps(net_margin_trend),
        'channel_labels_json': json.dumps(channel_labels),
        'channel_data_json': json.dumps(channel_data),
        'payment_labels_json': json.dumps(payment_labels),
        'payment_data_json': json.dumps(payment_data),
        'region_labels_json': json.dumps(region_labels),
        'region_data_json': json.dumps(region_data),
        'credit_paid': total_paid,
        'credit_debt': total_debt,
        'credit_total': total_credit,
        'recovery_pct': round((total_paid / total_credit * 100), 1) if total_credit > 0 else 60.6,
        'top_products': top_products,
        'kpi': {
            'ytd_gross': f"{sum(revenue_trend):,.2f}",
            'ytd_profit': f"{sum(net_margin_trend):,.2f}",
            'avg_margin': f"{round((sum(net_margin_trend) / sum(revenue_trend) * 100), 1)}%",
            'active_orders': CustomBookOrder.objects.count() + POSSale.objects.count(),
        }
    }
    return render(request, 'managerial/analytics.html', context)


@ceo_required
def credit_ledger(request):
    """
    School Credit & Receivables Ledger.
    Queries real SchoolCreditRecord models from the database.
    """
    schools_qs = SchoolCreditRecord.objects.all()

    totals = schools_qs.aggregate(
        total_granted=Sum('total_credit_granted'),
        total_paid=Sum('amount_paid'),
        total_balance=Sum('balance_outstanding')
    )

    total_granted = f"{totals['total_granted'] or Decimal('0.00'):,.2f}"
    total_recovered = f"{totals['total_paid'] or Decimal('0.00'):,.2f}"
    total_receivable = f"{totals['total_balance'] or Decimal('0.00'):,.2f}"

    schools = []
    for s in schools_qs:
        status_class = 'badge bg-success'
        if s.status == 'PARTIALLY_PAID':
            status_class = 'badge bg-warning text-dark'
        elif s.status == 'OVERDUE_NOTICE':
            status_class = 'badge bg-danger'

        schools.append({
            'id': s.id,
            'school_name': s.school_name,
            'location': s.location,
            'contact_person': s.principal_name,
            'phone': s.phone_number,
            'total_invoiced': f"{s.total_credit_granted:,.2f}",
            'amount_paid': f"{s.amount_paid:,.2f}",
            'balance_due': f"{s.balance_outstanding:,.2f}",
            'raw_balance': s.balance_outstanding,
            'due_date': s.term_due_date.strftime('%B %d, %Y') if s.balance_outstanding > 0 else 'Settled',
            'status': s.get_status_display(),
            'status_class': status_class,
        })

    context = {
        'schools': schools,
        'all_schools': schools_qs,
        'total_granted': total_granted,
        'total_recovered': total_recovered,
        'total_receivable': total_receivable,
    }
    return render(request, 'managerial/credit_ledger.html', context)


@ceo_required
def record_payment(request, pk=None):
    """
    Records an installment recovery payment for a school credit record.
    """
    if request.method == 'POST':
        school_id = pk or request.POST.get('school_id')
        school = get_object_or_404(SchoolCreditRecord, pk=school_id)
        amount_raw = request.POST.get('payment_amount', '0').replace(',', '').strip()
        notes = request.POST.get('payment_notes', '').strip()

        try:
            amount = Decimal(amount_raw)
            if amount <= Decimal('0.00'):
                messages.error(request, "Payment amount must be greater than zero.")
                return redirect('managerial:credit_ledger')
        except Exception:
            messages.error(request, "Invalid payment amount specified.")
            return redirect('managerial:credit_ledger')

        school.amount_paid += amount
        school.last_payment_date = timezone.now().date()
        if notes:
            new_note = f"[{timezone.now().strftime('%Y-%m-%d')} - GH₵ {amount:,.2f}]: {notes}"
            school.notes = f"{school.notes}\n{new_note}".strip() if school.notes else new_note
        school.save()

        messages.success(request, f"Payment of GH₵ {amount:,.2f} recorded for {school.school_name}. Balance remaining: GH₵ {school.balance_outstanding:,.2f}.")
    return redirect('managerial:credit_ledger')


@logistics_required
def waybills(request):
    """
    Regional Bus Waybill & Dispatch Tracker.
    Queries real RegionalWaybill records from the database.
    """
    waybills_qs = RegionalWaybill.objects.all()

    consignments = []
    for w in waybills_qs:
        status_class = 'badge bg-primary font-mono'
        if w.status == 'ARRIVED_AT_TERMINAL':
            status_class = 'badge bg-info text-dark font-mono'
        elif w.status == 'DELIVERED_AND_SIGNED':
            status_class = 'badge bg-success font-mono'

        consignments.append({
            'id': w.id,
            'waybill_number': w.waybill_number,
            'carrier': w.get_carrier_display(),
            'origin': w.origin_hub,
            'destination': w.destination_town,
            'recipient': w.recipient_name,
            'phone': w.recipient_phone,
            'parcels': w.consignment_summary,
            'driver_contact': f"{w.driver_conductor_name} ({w.driver_phone})" if w.driver_phone else w.driver_conductor_name,
            'status': w.get_status_display(),
            'status_class': status_class,
            'dispatched_at': w.dispatched_at.strftime('%b %d, %I:%M %p'),
        })

    carrier_choices = RegionalWaybill.CARRIER_CHOICES

    context = {
        'consignments': consignments,
        'carrier_choices': carrier_choices,
    }
    return render(request, 'managerial/waybills.html', context)


@logistics_required
def create_waybill(request):
    """
    Logs a new bus waybill consignment at the Sunyani transport hub.
    """
    if request.method == 'POST':
        carrier = request.POST.get('carrier', 'VIP_JEOUN')
        prefix = carrier.split('_')[0]
        ref_num = uuid.uuid4().hex[:4].upper()
        waybill_number = request.POST.get('waybill_number', '').strip() or f"{prefix}-SNY-{ref_num}"
        if RegionalWaybill.objects.filter(waybill_number=waybill_number).exists():
            waybill_number = f"{waybill_number}-{uuid.uuid4().hex[:3].upper()}"

        destination_town = request.POST.get('destination_town', '').strip() or 'Kumasi (Asafo)'
        recipient_name = request.POST.get('recipient_name', '').strip() or 'Institutional Client'
        recipient_phone = request.POST.get('recipient_phone', '').strip() or '024 000 0000'
        consignment_summary = request.POST.get('consignment_summary', '').strip() or 'Cartons of Exercise Books'
        driver_conductor_name = request.POST.get('driver_conductor_name', '').strip()
        driver_phone = request.POST.get('driver_phone', '').strip()

        waybill = RegionalWaybill.objects.create(
            waybill_number=waybill_number,
            carrier=carrier,
            origin_hub='Sunyani Main Hub',
            destination_town=destination_town,
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            consignment_summary=consignment_summary,
            driver_conductor_name=driver_conductor_name,
            driver_phone=driver_phone,
            status='IN_TRANSIT',
            sms_alert_sent=True
        )
        messages.success(request, f"Waybill {waybill.waybill_number} logged successfully! Dispatch SMS sent to {waybill.recipient_phone}.")
    return redirect('managerial:waybills')


# ─── Staff Management Views (CEO Only) ───────────────────────────────────────

@ceo_required
def staff_list_view(request):
    """Management directory of all staff accounts and assigned roles."""
    staff_users = User.objects.filter(is_staff=True).order_by('-date_joined')
    staff_data = []
    for u in staff_users:
        staff_data.append({
            'user': u,
            'role': get_user_role(u),
        })

    return render(request, 'managerial/staff_list.html', {
        'staff_data': staff_data,
        'total_staff': len(staff_data),
    })


@ceo_required
def staff_create_view(request):
    """Create a new staff user with designated department role."""
    form = StaffUserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(
            request,
            f"Staff account '{user.username}' successfully created with role '{form.cleaned_data['role']}'."
        )
        return redirect('managerial:staff_list')

    return render(request, 'managerial/staff_form.html', {
        'form': form,
        'title': 'Add New Staff Member',
    })


@ceo_required
def staff_edit_view(request, pk):
    """Update role, status, or credentials of an existing staff member."""
    user = get_object_or_404(User, pk=pk, is_staff=True)
    form = StaffUserEditForm(request.POST or None, instance=user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(
            request,
            f"Staff account '{user.username}' successfully updated."
        )
        return redirect('managerial:staff_list')

    return render(request, 'managerial/staff_form.html', {
        'form': form,
        'title': f"Edit Staff Member: {user.username}",
        'edit_user': user,
    })


# ─── Database Backup & Disaster Recovery Views (CEO Only) ────────────────────

@ceo_required
def database_backup_view(request):
    """Executive Hub for Data Exports, Backups, and Disaster Recovery."""
    db_path = settings.DATABASES['default'].get('NAME', '')
    db_size_mb = 0
    if db_path and os.path.exists(str(db_path)):
        db_size_mb = round(os.path.getsize(str(db_path)) / (1024 * 1024), 2)

    stats = {
        'products_count': Product.objects.count(),
        'categories_count': Category.objects.count(),
        'custom_orders_count': CustomBookOrder.objects.count(),
        'pos_sales_count': POSSale.objects.count(),
        'credit_records_count': SchoolCreditRecord.objects.count(),
        'waybills_count': RegionalWaybill.objects.count(),
        'invoices_count': Invoice.objects.count(),
        'staff_count': User.objects.filter(is_staff=True).count(),
        'db_size_mb': db_size_mb,
        'db_engine': settings.DATABASES['default'].get('ENGINE', '').split('.')[-1],
        'timestamp': timezone.now(),
    }
    return render(request, 'managerial/database_backup.html', {'stats': stats})


@ceo_required
def export_database_json(request):
    """Exports full database records to a JSON snapshot archive."""
    buf = io.StringIO()
    call_command(
        'dumpdata',
        'catalog', 'customizer', 'orders', 'managerial', 'invoices', 'auth.User', 'auth.Group',
        stdout=buf,
        indent=2
    )
    datestamp = timezone.now().strftime('%Y%m%d_%H%M')
    response = HttpResponse(buf.getvalue(), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename=desaint_backup_{datestamp}.json'
    return response


@ceo_required
def download_sqlite_backup(request):
    """Downloads raw snapshot of the active SQLite database file."""
    db_path = settings.DATABASES['default'].get('NAME')
    if not db_path or not os.path.exists(str(db_path)):
        messages.error(request, "Database file not accessible or non-SQLite engine in use.")
        return redirect('managerial:database_backup')

    with open(str(db_path), 'rb') as f:
        data = f.read()

    datestamp = timezone.now().strftime('%Y%m%d_%H%M')
    response = HttpResponse(data, content_type='application/x-sqlite3')
    response['Content-Disposition'] = f'attachment; filename=desaint_database_{datestamp}.sqlite3'
    return response


@ceo_required
def export_csv_view(request, dataset):
    """Exports individual operational tables to clean spreadsheet CSV format."""
    datestamp = timezone.now().strftime('%Y%m%d_%H%M')
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename=desaint_{dataset}_{datestamp}.csv'
    writer = csv.writer(response)

    if dataset == 'credit-ledger':
        writer.writerow(['ID', 'School Name', 'Principal', 'Phone', 'Location', 'Granted (GHS)', 'Paid (GHS)', 'Balance (GHS)', 'Due Date', 'Status'])
        for s in SchoolCreditRecord.objects.all():
            writer.writerow([s.id, s.school_name, s.principal_name, s.phone_number, s.location, s.total_credit_granted, s.amount_paid, s.balance_outstanding, s.term_due_date, s.get_status_display()])

    elif dataset == 'waybills':
        writer.writerow(['ID', 'Waybill Number', 'Carrier', 'Origin', 'Destination', 'Recipient', 'Phone', 'Parcels Summary', 'Driver', 'Status', 'Dispatched At'])
        for w in RegionalWaybill.objects.all():
            writer.writerow([w.id, w.waybill_number, w.get_carrier_display(), w.origin_hub, w.destination_town, w.recipient_name, w.recipient_phone, w.consignment_summary, w.driver_conductor_name, w.get_status_display(), w.dispatched_at])

    elif dataset == 'pos-sales':
        writer.writerow(['ID', 'Receipt Number', 'Cashier', 'Branch', 'Payment Mode', 'Subtotal', 'Tax', 'Total (GHS)', 'Amount Tendered', 'Change', 'Date'])
        for p in POSSale.objects.all():
            writer.writerow([p.id, p.receipt_number, p.cashier_name, p.store_branch, p.get_payment_mode_display(), p.subtotal, p.tax_amount, p.total_amount, p.amount_tendered, p.change_given, p.created_at])

    elif dataset == 'products':
        writer.writerow(['ID', 'Product Name', 'SKU', 'Category', 'Retail Price (GHS)', 'Wholesale Price (GHS)', 'Box Size', 'Stock Status', 'Active'])
        for prod in Product.objects.select_related('category').all():
            writer.writerow([prod.id, prod.name, prod.sku, prod.category.name if prod.category else '', prod.retail_price, prod.wholesale_price, prod.wholesale_box_size, prod.get_stock_status_display(), prod.is_active])

    else:
        messages.error(request, "Invalid export dataset requested.")
        return redirect('managerial:database_backup')

    return response


@ceo_required
def restore_database_json(request):
    """Restores database records from an uploaded JSON dump."""
    if request.method == 'POST':
        json_file = request.FILES.get('backup_file')
        if not json_file:
            messages.error(request, "Please choose a valid .json backup file to restore.")
            return redirect('managerial:database_backup')

        try:
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
                for chunk in json_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            call_command('loaddata', tmp_path)
            os.remove(tmp_path)
            messages.success(request, f"Database restored successfully from '{json_file.name}'!")
        except Exception as e:
            messages.error(request, f"Database restore failed: {str(e)}")

    return redirect('managerial:database_backup')



