import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from .cart import Cart
from .models import POSSale
from catalog.models import Product, Category
from invoices.models import Invoice, InvoiceItem
from core.decorators import cashier_required

@cashier_required
def pos_terminal(request):
    """
    Sunyani Walk-in Store Point-of-Sale (POS) Terminal.
    Optimized for fast counter sales with thermal receipt printing.
    """
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.filter(is_active=True)
    recent_sales = POSSale.objects.all()[:8]

    cashier_display = request.user.get_full_name() or request.user.username
    if cashier_display == 'admin':
        cashier_display = 'Mr. Solomon (CEO)'
    else:
        cashier_display = f"{cashier_display} (Sunyani Counter)"

    context = {
        'items': products,
        'categories': categories,
        'cashier_name': cashier_display,
        'recent_sales': recent_sales,
    }
    return render(request, 'orders/pos_terminal.html', context)


@cashier_required
@require_POST
def pos_submit_sale(request):
    """
    AJAX endpoint for submitting a completed POS counter sale.
    Creates a persistent POSSale record in the database with tender & change logging.
    """
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        total_amount = Decimal(str(data.get('total_amount', '0.00')))
        amount_tendered = Decimal(str(data.get('amount_tendered', total_amount)))
        change_given = max(Decimal('0.00'), amount_tendered - total_amount)
        payment_mode = data.get('payment_mode', 'CASH')
        
        cashier = request.user.get_full_name() or request.user.username
        if not cashier or cashier == 'admin':
            cashier = data.get('cashier_name', 'Mr. Solomon (CEO)')
            
        receipt_num = f"DSP-POS-{timezone.now().strftime('%m%d')}-{POSSale.objects.count() + 101}"

        sale = POSSale.objects.create(
            receipt_number=receipt_num,
            cashier_name=cashier,
            store_branch='Sunyani Main Branch',
            payment_mode=payment_mode,
            subtotal=total_amount,
            tax_amount=Decimal('0.00'),
            total_amount=total_amount,
            amount_tendered=amount_tendered,
            change_given=change_given,
            items_summary=json.dumps(items)
        )

        return JsonResponse({
            'success': True,
            'sale_id': sale.pk,
            'receipt_number': sale.receipt_number,
            'receipt_url': f"/admin/pos/receipt/{sale.pk}/",
            'total_amount': f"{sale.total_amount:.2f}",
            'amount_tendered': f"{sale.amount_tendered:.2f}",
            'change_given': f"{sale.change_given:.2f}",
            'payment_mode': sale.get_payment_mode_display(),
            'cashier_name': sale.cashier_name,
            'created_at': sale.created_at.strftime('%b %d, %Y %I:%M %p')
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@cashier_required
def pos_receipt_detail(request, pk):
    """
    Dedicated printable thermal / A4 receipt slip view for a completed POS counter sale.
    Optimized for standalone display and print dialogs without UI wrapper clipping.
    """
    sale = get_object_or_404(POSSale, pk=pk)
    items = sale.parsed_items
    auto_print = request.GET.get('print', 'false').lower() == 'true'

    context = {
        'sale': sale,
        'items': items,
        'auto_print': auto_print,
    }
    return render(request, 'orders/pos_receipt_print.html', context)


@cashier_required
def pos_history(request):
    """
    Cashier Daily Till Log and Transaction History.
    """
    sales = POSSale.objects.all()
    today_sales = sales.filter(created_at__date=timezone.now().date())
    total_cash = sum(s.total_amount for s in today_sales if s.payment_mode == 'CASH')
    total_momo = sum(s.total_amount for s in today_sales if s.payment_mode == 'MOMO_TILL')
    total_today = sum(s.total_amount for s in today_sales)

    context = {
        'sales': sales,
        'today_sales': today_sales,
        'total_cash': total_cash,
        'total_momo': total_momo,
        'total_today': total_today,
    }
    return render(request, 'orders/pos_history.html', context)


def cart_detail(request):
    """
    Shopping Cart View.
    """
    cart = Cart(request)
    return render(request, 'orders/cart.html', {'cart': cart})


@require_POST
def cart_add(request, product_id):
    """
    Add a product to the session cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    override = request.POST.get('override', 'false').lower() == 'true'
    cart.add(product=product, quantity=quantity, override_quantity=override)
    messages.success(request, f"Added {product.name} to cart.")
    return redirect('orders_public:cart_detail')


@require_POST
def cart_remove(request, product_id):
    """
    Remove a product from the session cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"Removed {product.name} from cart.")
    return redirect('orders_public:cart_detail')


def checkout(request):
    """
    Multi-Channel Checkout View for Retail & B2B Wholesale.
    """
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('core:home')

    if request.method == 'POST':
        client_name = request.POST.get('client_name', '').strip()
        client_phone = request.POST.get('client_phone', '').strip()
        delivery_address = request.POST.get('delivery_address', '').strip()
        channel_type = request.POST.get('channel_type', 'RETAIL_RECEIPT')
        payment_method = request.POST.get('payment_method', 'CASH')
        notes = request.POST.get('notes', '').strip()

        if not client_name or not client_phone:
            messages.error(request, "Please provide your full name and active phone number.")
            return render(request, 'orders/checkout.html', {'cart': cart})

        subtotal = cart.get_total_price()
        invoice_ref = f"DSP-INV-{timezone.now().strftime('%Y%m')}-{Invoice.objects.count() + 101}"

        invoice = Invoice.objects.create(
            invoice_number=invoice_ref,
            invoice_type=channel_type,
            tax_mode='RETAIL_NET' if channel_type == 'RETAIL_RECEIPT' else 'INSTITUTIONAL_WHT_3PCT',
            client_name=client_name,
            client_phone=client_phone,
            subtotal=subtotal,
            total_payable=subtotal,
            payment_method=payment_method,
            notes=f"Delivery to: {delivery_address}. {notes}"
        )

        for item in cart:
            InvoiceItem.objects.create(
                invoice=invoice,
                description=item['name'],
                quantity=item['quantity'],
                unit_price=item['price'],
                total_price=item['total_price']
            )

        cart.clear()
        messages.success(request, f"Order {invoice_ref} submitted successfully!")
        return redirect('orders_public:order_confirmation', pk=invoice.pk)

    return render(request, 'orders/checkout.html', {'cart': cart})


def order_confirmation(request, pk):
    """
    Order Confirmation & Printable Proforma View.
    """
    invoice = get_object_or_404(Invoice.objects.prefetch_related('items'), pk=pk)
    return render(request, 'orders/order_confirmation.html', {'invoice': invoice})
