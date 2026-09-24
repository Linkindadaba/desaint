from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from decimal import Decimal
import uuid

from core.decorators import staff_required, ceo_required
from .models import Product, Category
from inventory.models import InventoryItem, Supplier, StockMovement


@staff_required
def product_list(request):
    """
    Catalog Management & Product Directory for Staff.
    Supports live search, category filtering, and direct CRUD operations.
    """
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()

    products_qs = Product.objects.select_related('category').prefetch_related('inventory').all()

    if query:
        products_qs = products_qs.filter(name__icontains=query) | products_qs.filter(sku__icontains=query)

    if category_id:
        products_qs = products_qs.filter(category_id=category_id)

    categories = Category.objects.filter(is_active=True)
    suppliers = Supplier.objects.filter(is_active=True)

    context = {
        'products': products_qs,
        'categories': categories,
        'suppliers': suppliers,
        'query': query,
        'selected_category': category_id,
        'total_products': products_qs.count(),
    }
    return render(request, 'catalog/product_list.html', context)


@staff_required
@require_POST
def product_create(request):
    """
    Creates a new Product in the catalog and optionally links an initial InventoryItem.
    """
    name = request.POST.get('name', '').strip()
    sku = request.POST.get('sku', '').strip()
    category_id = request.POST.get('category')
    retail_price_raw = request.POST.get('retail_price', '0').replace(',', '').strip()
    wholesale_price_raw = request.POST.get('wholesale_price', '0').replace(',', '').strip()
    wholesale_box_size = request.POST.get('wholesale_box_size', 'Box of 120').strip()
    description = request.POST.get('description', '').strip()
    icon_class = request.POST.get('icon_class', 'fas fa-book').strip()
    is_customizable = request.POST.get('is_customizable') == 'on'

    if not name or not category_id:
        messages.error(request, "Product name and category are required.")
        return redirect('catalog:product_list')

    category = get_object_or_404(Category, pk=category_id)

    if not sku:
        sku = f"DSP-{uuid.uuid4().hex[:6].upper()}"
    elif Product.objects.filter(sku=sku).exists():
        messages.error(request, f"A product with SKU '{sku}' already exists.")
        return redirect('catalog:product_list')

    slug = slugify(name)
    if Product.objects.filter(slug=slug).exists():
        slug = f"{slug}-{uuid.uuid4().hex[:4]}"

    try:
        retail_price = Decimal(retail_price_raw)
        wholesale_price = Decimal(wholesale_price_raw)
    except Exception:
        messages.error(request, "Invalid prices entered.")
        return redirect('catalog:product_list')

    product = Product(
        name=name,
        slug=slug,
        category=category,
        sku=sku,
        description=description,
        retail_price=retail_price,
        wholesale_price=wholesale_price,
        wholesale_box_size=wholesale_box_size,
        icon_class=icon_class,
        is_customizable=is_customizable,
        stock_status='IN_STOCK',
        stock_quantity=0
    )

    if 'image' in request.FILES:
        product.image = request.FILES['image']

    product.save()

    # Optional: Automatically initialize InventoryItem if supplied
    supplier_id = request.POST.get('supplier_id')
    cost_price_raw = request.POST.get('cost_price', '0').replace(',', '').strip()
    cartons = int(request.POST.get('carton_stock', 0) or 0)
    loose = int(request.POST.get('loose_stock', 0) or 0)
    pieces_per_carton = int(request.POST.get('pieces_per_carton', 120) or 120)
    bulk_unit_name = request.POST.get('bulk_unit_name', 'Carton').strip() or 'Carton'
    retail_unit_name = request.POST.get('retail_unit_name', 'Piece').strip() or 'Piece'
    warehouse_location = request.POST.get('warehouse_location', 'Sunyani Main Hub').strip()

    supplier = None
    if supplier_id:
        supplier = Supplier.objects.filter(pk=supplier_id).first()

    cost_price = Decimal(cost_price_raw) if cost_price_raw else Decimal('0.00')

    inv = InventoryItem.objects.create(
        product=product,
        supplier=supplier,
        cost_price=cost_price,
        bulk_unit_name=bulk_unit_name,
        retail_unit_name=retail_unit_name,
        pieces_per_carton=pieces_per_carton,
        carton_stock=cartons,
        loose_stock=loose,
        warehouse_location=warehouse_location
    )
    inv.sync_to_catalog()

    if cartons > 0 or loose > 0:
        StockMovement.objects.create(
            item=inv,
            movement_type='RESTOCK_IN',
            carton_delta=cartons,
            loose_delta=loose,
            resulting_carton_stock=cartons,
            resulting_loose_stock=loose,
            reference='INITIAL-ONBOARDING',
            created_by=request.user,
            note=f"Initial inventory onboarding for '{product.name}'."
        )

    messages.success(request, f"Product '{product.name}' (SKU: {product.sku}) created and linked to warehouse inventory.")
    return redirect('catalog:product_list')


@staff_required
@require_POST
def product_edit(request, pk):
    """
    Updates an existing Product's information, prices, and image.
    """
    product = get_object_or_404(Product, pk=pk)

    name = request.POST.get('name', '').strip()
    if name:
        product.name = name

    category_id = request.POST.get('category')
    if category_id:
        product.category = get_object_or_404(Category, pk=category_id)

    retail_raw = request.POST.get('retail_price', '').replace(',', '').strip()
    if retail_raw:
        try:
            product.retail_price = Decimal(retail_raw)
        except Exception:
            pass

    wholesale_raw = request.POST.get('wholesale_price', '').replace(',', '').strip()
    if wholesale_raw:
        try:
            product.wholesale_price = Decimal(wholesale_raw)
        except Exception:
            pass

    product.wholesale_box_size = request.POST.get('wholesale_box_size', product.wholesale_box_size).strip()
    product.description = request.POST.get('description', product.description).strip()
    product.icon_class = request.POST.get('icon_class', product.icon_class).strip()
    product.is_customizable = request.POST.get('is_customizable') == 'on'
    product.is_active = request.POST.get('is_active') == 'on'

    stock_status = request.POST.get('stock_status')
    if stock_status in dict(Product.STOCK_STATUS_CHOICES):
        product.stock_status = stock_status

    if 'image' in request.FILES:
        product.image = request.FILES['image']

    product.save()

    messages.success(request, f"Product '{product.name}' updated successfully.")
    return redirect('catalog:product_list')


@staff_required
@require_POST
def product_delete(request, pk):
    """
    Deletes a Product and associated inventory records.
    """
    product = get_object_or_404(Product, pk=pk)
    name = product.name
    product.delete()
    messages.info(request, f"Product '{name}' and its inventory ledger were deleted.")
    return redirect('catalog:product_list')


@staff_required
@require_POST
def category_create(request):
    """
    Creates a new Product Category.
    """
    name = request.POST.get('name', '').strip()
    icon_class = request.POST.get('icon_class', 'fas fa-book').strip()
    if name:
        slug = slugify(name)
        cat, created = Category.objects.get_or_create(
            slug=slug,
            defaults={'name': name, 'icon_class': icon_class}
        )
        if created:
            messages.success(request, f"Category '{cat.name}' created.")
        else:
            messages.info(request, f"Category '{cat.name}' already exists.")
    return redirect('catalog:product_list')
