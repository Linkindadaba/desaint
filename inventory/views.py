from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Q
from django.views.decorators.http import require_POST
from decimal import Decimal

from core.decorators import staff_required, ceo_required
from catalog.models import Category, Product
from .models import InventoryItem, Supplier, StockMovement


@staff_required
def dashboard(request):
    """
    Real-Time Warehouse & Stock Valuation Command Center.
    Provides KPIs, safety reorder warnings, recent movement trail, and quick unboxing controls.
    """
    items = InventoryItem.objects.select_related('product', 'product__category', 'supplier').all()

    total_cartons = sum(it.carton_stock for it in items)
    total_loose = sum(it.loose_stock for it in items)
    total_pieces = sum(it.total_retail_pieces for it in items)
    total_cost_val = sum(it.total_cost_valuation for it in items)
    total_retail_val = sum(it.total_retail_valuation for it in items)

    low_stock_items = [it for it in items if it.is_low_stock]
    out_of_stock_items = [it for it in items if it.total_retail_pieces == 0]

    recent_movements = StockMovement.objects.select_related(
        'item__product', 'created_by'
    ).order_by('-created_at')[:10]

    suppliers_count = Supplier.objects.filter(is_active=True).count()

    context = {
        'items': items,
        'total_cartons': total_cartons,
        'total_loose': total_loose,
        'total_pieces': total_pieces,
        'total_cost_val': total_cost_val,
        'total_retail_val': total_retail_val,
        'potential_gross_margin': total_retail_val - total_cost_val,
        'low_stock_items': low_stock_items,
        'low_stock_count': len(low_stock_items),
        'out_of_stock_count': len(out_of_stock_items),
        'suppliers_count': suppliers_count,
        'recent_movements': recent_movements,
    }
    return render(request, 'inventory/dashboard.html', context)


@staff_required
def stock_ledger(request):
    """
    Complete Authoritative Stock Balance Ledger.
    Tabular display with search, category filtering, and direct modal controls for restock/unboxing/audits.
    """
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
    status_filter = request.GET.get('status', '').strip()

    items = InventoryItem.objects.select_related('product', 'product__category', 'supplier').all()

    if query:
        items = items.filter(
            Q(product__name__icontains=query) |
            Q(product__sku__icontains=query) |
            Q(warehouse_location__icontains=query) |
            Q(supplier__name__icontains=query)
        )

    if category_id:
        items = items.filter(product__category_id=category_id)

    # Filter in Python for computed properties if status specified
    if status_filter == 'LOW':
        items = [it for it in items if it.is_low_stock and it.total_retail_pieces > 0]
    elif status_filter == 'OUT':
        items = [it for it in items if it.total_retail_pieces == 0]
    elif status_filter == 'OK':
        items = [it for it in items if not it.is_low_stock and it.total_retail_pieces > 0]

    categories = Category.objects.filter(is_active=True)
    suppliers = Supplier.objects.filter(is_active=True)

    context = {
        'items': items,
        'categories': categories,
        'suppliers': suppliers,
        'query': query,
        'selected_category': category_id,
        'status_filter': status_filter,
    }
    return render(request, 'inventory/ledger.html', context)


@staff_required
def movements_log(request):
    """
    Stock Movement Audit Log.
    Chronological ledger tracking every restock, POS deduction, break-bulk, and audit adjustment.
    """
    movement_type = request.GET.get('type', '').strip()
    query = request.GET.get('q', '').strip()

    movements = StockMovement.objects.select_related('item__product', 'created_by').order_by('-created_at')

    if movement_type:
        movements = movements.filter(movement_type=movement_type)

    if query:
        movements = movements.filter(
            Q(item__product__name__icontains=query) |
            Q(item__product__sku__icontains=query) |
            Q(reference__icontains=query) |
            Q(note__icontains=query)
        )

    context = {
        'movements': movements[:200],
        'movement_types': StockMovement.MOVEMENT_TYPES,
        'selected_type': movement_type,
        'query': query,
    }
    return render(request, 'inventory/movements.html', context)


@staff_required
def suppliers_view(request):
    """
    Suppliers & Commercial Distributors Directory.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        contact_person = request.POST.get('contact_person', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()

        if name and phone:
            Supplier.objects.create(
                name=name,
                contact_person=contact_person,
                phone=phone,
                email=email,
                address=address
            )
            messages.success(request, f"Supplier '{name}' registered successfully.")
            return redirect('inventory:suppliers')
        else:
            messages.error(request, "Supplier name and phone number are required.")

    suppliers = Supplier.objects.prefetch_related('inventory_items__product').all()
    return render(request, 'inventory/suppliers.html', {'suppliers': suppliers})


# ─── Operational Actions (Stock Inflow, Unbox, Reconcile) ────────────────────

@staff_required
@require_POST
def restock_item(request, pk):
    """
    Receives incoming stock into Sunyani warehouse from production or supplier delivery.
    """
    item = get_object_or_404(InventoryItem, pk=pk)
    cartons = int(request.POST.get('cartons', 0) or 0)
    loose = int(request.POST.get('loose', 0) or 0)
    cost = request.POST.get('cost_price', '').strip()
    cost_price = Decimal(cost) if cost else None
    reference = request.POST.get('reference', '').strip() or 'SUPPLIER-DELIVERY'
    note = request.POST.get('note', '').strip()

    if cartons <= 0 and loose <= 0:
        messages.warning(request, "Please specify a positive carton or loose quantity to restock.")
        return redirect('inventory:ledger')

    item.restock(
        cartons=cartons,
        loose_pieces=loose,
        cost_price=cost_price,
        user=request.user,
        reference=reference,
        note=note
    )
    messages.success(
        request,
        f"Restocked {cartons} {item.bulk_unit_name}(s) and {loose} {item.retail_unit_name}(s) for '{item.product.name}'."
    )
    return redirect('inventory:ledger')


@staff_required
@require_POST
def break_bulk_unbox(request, pk):
    """
    Unboxes sealed bulk warehouse cartons into counter loose shelf units.
    """
    item = get_object_or_404(InventoryItem, pk=pk)
    cartons_to_unbox = int(request.POST.get('cartons_to_unbox', 1) or 1)

    if cartons_to_unbox <= 0:
        messages.warning(request, "Please enter at least 1 carton to unbox.")
        return redirect('inventory:ledger')

    if cartons_to_unbox > item.carton_stock:
        messages.error(
            request,
            f"Cannot unbox {cartons_to_unbox} cartons. Only {item.carton_stock} {item.bulk_unit_name}(s) in warehouse."
        )
        return redirect('inventory:ledger')

    unboxed_pieces = cartons_to_unbox * item.pieces_per_carton
    item.carton_stock -= cartons_to_unbox
    item.loose_stock += unboxed_pieces
    item.save(update_fields=['carton_stock', 'loose_stock', 'updated_at'])

    StockMovement.objects.create(
        item=item,
        movement_type='BREAK_BULK',
        carton_delta=-cartons_to_unbox,
        loose_delta=unboxed_pieces,
        resulting_carton_stock=item.carton_stock,
        resulting_loose_stock=item.loose_stock,
        reference='MANUAL-UNBOX',
        created_by=request.user,
        note=f"Manual shelf replenishment: unboxed {cartons_to_unbox} {item.bulk_unit_name}(s) into {unboxed_pieces} {item.retail_unit_name}(s)."
    )

    item.sync_to_catalog()

    messages.success(
        request,
        f"Unboxed {cartons_to_unbox} {item.bulk_unit_name}(s) into {unboxed_pieces} loose {item.retail_unit_name}(s) on shelf."
    )
    return redirect('inventory:ledger')


@staff_required
@require_POST
def adjust_stock(request, pk):
    """
    Reconciles physical count discrepancies with automated variance logging.
    """
    item = get_object_or_404(InventoryItem, pk=pk)
    new_cartons = int(request.POST.get('new_cartons', item.carton_stock) or 0)
    new_loose = int(request.POST.get('new_loose', item.loose_stock) or 0)
    reason = request.POST.get('reason', 'Periodic Physical Stocktake').strip()
    note = request.POST.get('note', '').strip()

    item.adjust_stock(
        new_carton_count=new_cartons,
        new_loose_count=new_loose,
        reason=reason,
        user=request.user,
        note=note
    )

    messages.success(
        request,
        f"Stock balance reconciled for '{item.product.name}': {item.carton_stock} {item.bulk_unit_name}(s), {item.loose_stock} {item.retail_unit_name}(s)."
    )
    return redirect('inventory:ledger')


@staff_required
@require_POST
def edit_supplier(request, pk):
    """
    Updates commercial supplier information and contact credentials.
    """
    supplier = get_object_or_404(Supplier, pk=pk)
    name = request.POST.get('name', '').strip()
    contact_person = request.POST.get('contact_person', '').strip()
    phone = request.POST.get('phone', '').strip()
    email = request.POST.get('email', '').strip()
    address = request.POST.get('address', '').strip()
    is_active = request.POST.get('is_active') == 'on'

    if not name or not phone:
        messages.error(request, "Supplier name and phone number are required.")
        return redirect('inventory:suppliers')

    supplier.name = name
    supplier.contact_person = contact_person
    supplier.phone = phone
    supplier.email = email
    supplier.address = address
    supplier.is_active = is_active
    supplier.save()

    messages.success(request, f"Supplier '{supplier.name}' updated successfully.")
    return redirect('inventory:suppliers')


@ceo_required
@require_POST
def delete_supplier(request, pk):
    """
    Deletes a supplier or detaches linked inventory records.
    """
    supplier = get_object_or_404(Supplier, pk=pk)
    name = supplier.name
    supplier.delete()
    messages.info(request, f"Supplier '{name}' was removed from procurement directory.")
    return redirect('inventory:suppliers')


@staff_required
@require_POST
def edit_item_config(request, pk):
    """
    Updates inventory packaging ratios, landed unit cost, safety reorder thresholds, and warehouse location.
    """
    item = get_object_or_404(InventoryItem, pk=pk)
    
    supplier_id = request.POST.get('supplier_id')
    cost_raw = request.POST.get('cost_price', '').replace(',', '').strip()
    bulk_unit_name = request.POST.get('bulk_unit_name', item.bulk_unit_name).strip()
    retail_unit_name = request.POST.get('retail_unit_name', item.retail_unit_name).strip()
    pieces_raw = request.POST.get('pieces_per_carton', '')
    threshold_raw = request.POST.get('low_stock_threshold_cartons', '')
    warehouse_location = request.POST.get('warehouse_location', item.warehouse_location).strip()

    if supplier_id:
        item.supplier = Supplier.objects.filter(pk=supplier_id).first()
    elif supplier_id == "":
        item.supplier = None

    if cost_raw:
        try:
            item.cost_price = Decimal(cost_raw)
        except Exception:
            pass

    if pieces_raw:
        try:
            pieces = int(pieces_raw)
            if pieces > 0:
                item.pieces_per_carton = pieces
        except Exception:
            pass

    if threshold_raw:
        try:
            item.low_stock_threshold_cartons = max(0, int(threshold_raw))
        except Exception:
            pass

    item.bulk_unit_name = bulk_unit_name or item.bulk_unit_name
    item.retail_unit_name = retail_unit_name or item.retail_unit_name
    item.warehouse_location = warehouse_location or item.warehouse_location
    item.save()

    messages.success(request, f"Configuration updated for '{item.product.name}'.")
    return redirect('inventory:ledger')

