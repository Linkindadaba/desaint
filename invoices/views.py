from django.shortcuts import render, get_object_or_404, redirect
from decimal import Decimal
from .models import Invoice, InvoiceItem
from core.decorators import ceo_required

@ceo_required
def invoice_proforma(request, pk):
    """
    Dedicated Printable A4 Institutional Proforma Invoice view.
    Renders official NDS commercial documentation compliant with Ghana GRA Act 896.
    """
    invoice = get_object_or_404(Invoice, pk=pk)
    items = invoice.items.all()

    # If items are empty, create or load items
    subtotal = invoice.subtotal
    if not items.exists() and subtotal > 0:
        pass

    context = {
        'invoice': invoice,
        'items': items,
        'subtotal_formatted': f"{invoice.subtotal:,.2f}",
        'wht_formatted': f"{invoice.wht_amount:,.2f}",
        'vat_formatted': f"{invoice.vat_amount:,.2f}",
        'total_payable_formatted': f"{invoice.total_payable:,.2f}",
    }
    return render(request, 'invoices/proforma_invoice.html', context)


@ceo_required
def invoice_sample(request):
    """
    Sample Proforma Invoice view for client preview and testing.
    Creates a sample institutional proforma if none exists in database.
    """
    invoice = Invoice.objects.filter(invoice_type='INSTITUTIONAL_PROFORMA').first()
    if not invoice:
        # Create a sample institutional proforma invoice
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

