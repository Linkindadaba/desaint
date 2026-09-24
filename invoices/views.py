from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Sum, Q
from decimal import Decimal
import uuid

from core.decorators import staff_required, ceo_required
from .models import Invoice, InvoiceItem


@staff_required
def invoice_list(request):
    """
    Invoices & Proforma Commercial Ledger.
    Allows searching, filtering by tax regime, tracking payment statuses, and issuing new proformas.
    """
    query = request.GET.get('q', '').strip()
    invoice_type = request.GET.get('type', '').strip()
    status_filter = request.GET.get('status', '').strip()

    invoices = Invoice.objects.prefetch_related('items').all()

    if query:
        invoices = invoices.filter(
            Q(invoice_number__icontains=query) |
            Q(client_name__icontains=query) |
            Q(client_tin__icontains=query) |
            Q(client_phone__icontains=query)
        )

    if invoice_type:
        invoices = invoices.filter(invoice_type=invoice_type)

    if status_filter == 'paid':
        invoices = invoices.filter(is_paid=True)
    elif status_filter == 'unpaid':
        invoices = invoices.filter(is_paid=False)

    # Financial Aggregations
    total_invoiced = sum(inv.total_payable for inv in invoices)
    total_paid = sum(inv.total_payable for inv in invoices if inv.is_paid)
    total_outstanding = total_invoiced - total_paid
    total_wht_withheld = sum(inv.wht_amount for inv in invoices)

    context = {
        'invoices': invoices,
        'query': query,
        'selected_type': invoice_type,
        'selected_status': status_filter,
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'total_outstanding': total_outstanding,
        'total_wht_withheld': total_wht_withheld,
        'invoice_types': Invoice.INVOICE_TYPE_CHOICES,
        'tax_modes': Invoice.TAX_MODE_CHOICES,
        'payment_methods': Invoice.PAYMENT_METHOD_CHOICES,
    }
    return render(request, 'invoices/invoice_list.html', context)


@staff_required
def invoice_proforma(request, pk):
    """
    Dedicated Printable A4 Institutional Proforma Invoice view.
    Renders official NDS commercial documentation compliant with Ghana GRA Act 896.
    """
    invoice = get_object_or_404(Invoice, pk=pk)
    items = invoice.items.all()

    context = {
        'invoice': invoice,
        'items': items,
        'subtotal_formatted': f"{invoice.subtotal:,.2f}",
        'wht_formatted': f"{invoice.wht_amount:,.2f}",
        'vat_formatted': f"{invoice.vat_amount:,.2f}",
        'total_payable_formatted': f"{invoice.total_payable:,.2f}",
    }
    return render(request, 'invoices/proforma_invoice.html', context)


@staff_required
@require_POST
def invoice_create(request):
    """
    Creates a new Commercial / Institutional Invoice or Proforma with line items.
    Automatically computes GRA statutory taxes (Act 896 3% WHT or standard VAT).
    """
    client_name = request.POST.get('client_name', '').strip()
    client_phone = request.POST.get('client_phone', '').strip()
    client_tin = request.POST.get('client_tin', '').strip()
    invoice_type = request.POST.get('invoice_type', 'INSTITUTIONAL_PROFORMA').strip()
    tax_mode = request.POST.get('tax_mode', 'INSTITUTIONAL_WHT_3PCT').strip()
    payment_method = request.POST.get('payment_method', 'BANK_TRANSFER').strip()
    notes = request.POST.get('notes', '').strip()

    if not client_name:
        messages.error(request, "Client or institution name is required.")
        return redirect('invoices:invoice_list')

    # Parse line items
    descriptions = request.POST.getlist('item_description[]')
    quantities = request.POST.getlist('item_quantity[]')
    unit_prices = request.POST.getlist('item_unit_price[]')

    parsed_items = []
    subtotal = Decimal('0.00')

    for desc, qty_str, price_str in zip(descriptions, quantities, unit_prices):
        desc = desc.strip()
        if not desc:
            continue
        try:
            qty = int(qty_str or 1)
            unit_price = Decimal(price_str.replace(',', '').strip() or '0.00')
            if qty > 0 and unit_price >= 0:
                line_total = Decimal(qty) * unit_price
                subtotal += line_total
                parsed_items.append({
                    'description': desc,
                    'quantity': qty,
                    'unit_price': unit_price,
                    'total_price': line_total,
                })
        except Exception:
            continue

    if not parsed_items:
        # Default single general item if none provided
        general_amount_raw = request.POST.get('general_amount', '0').replace(',', '').strip()
        try:
            gen_amt = Decimal(general_amount_raw)
            if gen_amt > 0:
                subtotal = gen_amt
                parsed_items.append({
                    'description': 'Stationery & Educational Printing Supplies',
                    'quantity': 1,
                    'unit_price': gen_amt,
                    'total_price': gen_amt,
                })
        except Exception:
            pass

    if not parsed_items:
        messages.error(request, "At least one valid line item with quantity and price is required.")
        return redirect('invoices:invoice_list')

    # Tax & Statutory Calculations
    vat_amount = Decimal('0.00')
    wht_amount = Decimal('0.00')

    if tax_mode == 'INSTITUTIONAL_WHT_3PCT':
        # Ghana Act 896 Section 116: 3% Withholding Tax on institutional supply of goods
        wht_amount = (subtotal * Decimal('0.03')).quantize(Decimal('0.01'))
        total_payable = subtotal - wht_amount
    elif tax_mode == 'GRA_STANDARD_VAT':
        # Standard GRA composite rate (~21.9% or 21% net)
        vat_amount = (subtotal * Decimal('0.21')).quantize(Decimal('0.01'))
        total_payable = subtotal + vat_amount
    else:
        # RETAIL_NET
        total_payable = subtotal

    # Generate Unique Invoice Number
    year = timezone.now().year
    prefix = 'PRO' if 'PROFORMA' in invoice_type else ('INV' if 'WHOLESALE' in invoice_type else 'REC')
    inv_number = f"{prefix}-{year}-NDS-{uuid.uuid4().hex[:6].upper()}"

    invoice = Invoice.objects.create(
        invoice_number=inv_number,
        invoice_type=invoice_type,
        tax_mode=tax_mode,
        client_name=client_name,
        client_phone=client_phone,
        client_tin=client_tin,
        subtotal=subtotal,
        vat_amount=vat_amount,
        wht_amount=wht_amount,
        total_payable=total_payable,
        payment_method=payment_method,
        notes=notes,
        is_paid=False,
    )

    for itm in parsed_items:
        InvoiceItem.objects.create(
            invoice=invoice,
            description=itm['description'],
            quantity=itm['quantity'],
            unit_price=itm['unit_price'],
            total_price=itm['total_price'],
        )

    messages.success(request, f"Invoice {inv_number} for {client_name} created successfully.")
    return redirect('invoices:proforma', pk=invoice.pk)


@staff_required
@require_POST
def invoice_mark_paid(request, pk):
    """
    Marks an invoice as paid and logs transaction/settlement reference.
    """
    invoice = get_object_or_404(Invoice, pk=pk)
    payment_reference = request.POST.get('payment_reference', '').strip()

    invoice.is_paid = True
    invoice.paid_at = timezone.now()
    if payment_reference:
        invoice.payment_reference = payment_reference
    invoice.save(update_fields=['is_paid', 'paid_at', 'payment_reference'])

    messages.success(request, f"Invoice {invoice.invoice_number} marked as PAID.")
    return redirect('invoices:invoice_list')


@ceo_required
@require_POST
def invoice_delete(request, pk):
    """
    Deletes an invoice and its line items. Restricted to CEO / Management.
    """
    invoice = get_object_or_404(Invoice, pk=pk)
    num = invoice.invoice_number
    invoice.delete()
    messages.info(request, f"Invoice {num} was deleted.")
    return redirect('invoices:invoice_list')


@staff_required
def invoice_sample(request):
    """
    Sample Proforma Invoice view for client preview and testing.
    Creates a sample institutional proforma if none exists in database.
    """
    invoice = Invoice.objects.filter(invoice_type='INSTITUTIONAL_PROFORMA').first()
    if not invoice:
        invoice = Invoice.objects.create(
            invoice_number='PRO-2026-STJ-0811',
            invoice_type='INSTITUTIONAL_PROFORMA',
            tax_mode='INSTITUTIONAL_WHT_3PCT',
            client_name='St. James Seminary Senior High School',
            client_phone='024 400 1122',
            client_tin='P0018924401',
            subtotal=Decimal('24000.00'),
            vat_amount=Decimal('0.00'),
            wht_amount=Decimal('720.00'),
            total_payable=Decimal('23280.00'),
            payment_method='BANK_TRANSFER',
            notes='Delivery to Sunyani campus via regional dispatch van. 3% WHT certificate to be remitted on final settlement.'
        )
        InvoiceItem.objects.create(
            invoice=invoice,
            description='Custom Exercise Books (80 Pages - Single Line Broad Ruling, 250gsm Laminated Full Color Cover)',
            quantity=7500,
            unit_price=Decimal('3.20')
        )
    return redirect('invoices:proforma', pk=invoice.pk)
