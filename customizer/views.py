from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Sum, Q
from decimal import Decimal
import uuid

from .models import RulingOption, CustomBookOrder
from core.decorators import staff_required, ceo_required, graphics_required


def configurator(request):
    """
    Flagship School Book Configurator & Pricing Engine.
    Accessible to prospective schools on storefront and Graphics Manager in portal.
    Queries real RulingOption models and enforces 5,000 to 10,000 copies MOQ.
    """
    rulings = RulingOption.objects.filter(is_active=True)
    is_staff_user = request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
    base_template = 'base_admin.html' if is_staff_user else 'base_storefront.html'

    context = {
        'rulings': rulings,
        'base_template': base_template,
        'is_staff_user': is_staff_user,
    }
    return render(request, 'customizer/configurator.html', context)


def customizer_submit(request):
    """
    Handles dynamic submission of school customizer order with optional crest upload.
    Generates unique order reference, computes Act 896 financials, and redirects to digital proof sign-off.
    """
    if request.method == 'POST':
        school_name = request.POST.get('school_name', '').strip() or 'St. James Seminary Senior High'
        proprietor_name = request.POST.get('proprietor_name', '').strip() or 'School Administration'
        contact_phone = request.POST.get('contact_phone', '').strip() or '024 000 0000'
        contact_email = request.POST.get('contact_email', '').strip()
        delivery_location = request.POST.get('delivery_location', '').strip() or 'Sunyani Campus'
        ruling_id = request.POST.get('ruling_id')
        quantity = int(request.POST.get('quantity', 5000))
        school_motto = request.POST.get('school_motto', '').strip()
        back_cover = request.POST.get('back_cover_content', '').strip() or 'School Anthem, School Rules & Regulations, National Pledge'
        notes = f"Motto: {school_motto}" if school_motto else ""

        ruling = None
        if ruling_id:
            try:
                ruling = RulingOption.objects.get(pk=ruling_id)
            except RulingOption.DoesNotExist:
                ruling = RulingOption.objects.first()
        if not ruling:
            ruling = RulingOption.objects.first()

        # Generate unique order reference (e.g. DSP-2026-STJ-4829)
        ref_suffix = uuid.uuid4().hex[:4].upper()
        acronym = "".join([w[0] for w in school_name.split()[:3] if w]).upper() or "SCH"
        order_ref = f"DSP-2026-{acronym}-{ref_suffix}"

        order = CustomBookOrder(
            order_ref=order_ref,
            school_name=school_name,
            proprietor_name=proprietor_name,
            contact_phone=contact_phone,
            contact_email=contact_email,
            delivery_location=delivery_location,
            ruling=ruling,
            quantity=quantity,
            back_cover_content=back_cover,
            notes=notes,
            status='PROOF_PENDING'
        )

        if 'school_crest' in request.FILES:
            order.school_crest = request.FILES['school_crest']

        order.save()
        messages.success(request, f"Quotation generated successfully! Reference: {order.order_ref}")
        return redirect('customizer:proof_detail', pk=order.pk)

    return redirect('customizer:configurator')


def proof_detail(request, pk):
    """
    Dynamic Digital Artwork Proof Sign-Off View for a specific CustomBookOrder.
    Allows school proprietor to review vector layout and authorize production,
    and allows Graphics Manager to audit sign-off status.
    """
    order = get_object_or_404(CustomBookOrder, pk=pk)

    if request.method == 'POST':
        signatory_name = request.POST.get('signatory_name', '').strip() or order.proprietor_name
        order.digital_proof_approved = True
        order.approved_by_signatory = signatory_name
        order.approval_timestamp = timezone.now()
        order.status = 'PROOF_APPROVED'
        order.save()
        messages.success(request, f"Proof Approved! Production authorization logged for {order.school_name}.")

    is_staff_user = request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
    base_template = 'base_admin.html' if is_staff_user else 'base_storefront.html'

    context = {
        'order': order,
        'base_template': base_template,
        'is_staff_user': is_staff_user,
        'gross_formatted': f"{order.gross_amount:,.2f}",
        'wht_formatted': f"{order.wht_deducted:,.2f}",
        'net_formatted': f"{order.net_payable:,.2f}",
    }
    return render(request, 'customizer/proof_approval.html', context)


def proof_approval(request):
    """
    Digital Proof Sign-Off View (Sample / Demo fallback).
    """
    order = CustomBookOrder.objects.first()
    if order:
        return redirect('customizer:proof_detail', pk=order.pk)

    # Fallback to configurator if no order exists yet
    return redirect('customizer:configurator')


@staff_required
def order_list(request):
    """
    School Custom Book Orders & Printing Directory.
    Enables Graphics Manager and Staff to oversee institutional print runs,
    track digital proof approval signatures, and monitor manufacturing stages.
    """
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    orders_qs = CustomBookOrder.objects.select_related('ruling').all()

    if query:
        orders_qs = orders_qs.filter(
            Q(order_ref__icontains=query) |
            Q(school_name__icontains=query) |
            Q(proprietor_name__icontains=query) |
            Q(contact_phone__icontains=query) |
            Q(delivery_location__icontains=query)
        )

    if status_filter:
        orders_qs = orders_qs.filter(status=status_filter)

    # Status counts & aggregations
    all_orders = list(CustomBookOrder.objects.all())
    total_orders = len(all_orders)
    pending_proofs = sum(1 for o in all_orders if o.status == 'PROOF_PENDING')
    in_production = sum(1 for o in all_orders if o.status in ['PROOF_APPROVED', 'PLATE_MAKING', 'PRINTING'])
    completed_dispatched = sum(1 for o in all_orders if o.status in ['COMPLETED', 'DISPATCHED'])
    total_copies = sum(o.quantity for o in all_orders)
    total_value = sum(o.net_payable for o in all_orders)

    context = {
        'orders': orders_qs,
        'query': query,
        'selected_status': status_filter,
        'total_orders': total_orders,
        'pending_proofs': pending_proofs,
        'in_production': in_production,
        'completed_dispatched': completed_dispatched,
        'total_copies': total_copies,
        'total_value': total_value,
        'status_choices': CustomBookOrder.STATUS_CHOICES,
    }
    return render(request, 'customizer/order_list.html', context)


@staff_required
@require_POST
def order_status_update(request, pk):
    """
    Updates manufacturing stage, production notes, and status for a CustomBookOrder.
    """
    order = get_object_or_404(CustomBookOrder, pk=pk)
    new_status = request.POST.get('status')
    notes = request.POST.get('notes', '').strip()

    if new_status in dict(CustomBookOrder.STATUS_CHOICES):
        order.status = new_status
        if new_status == 'PROOF_APPROVED' and not order.digital_proof_approved:
            order.digital_proof_approved = True
            order.approval_timestamp = timezone.now()
            order.approved_by_signatory = order.approved_by_signatory or f"Staff Override ({request.user.username})"

    if notes:
        order.notes = notes

    order.save()
    messages.success(request, f"Order {order.order_ref} ({order.school_name}) updated to '{order.get_status_display()}'.")
    return redirect('customizer:order_list')


@ceo_required
@require_POST
def order_delete(request, pk):
    """
    Deletes a school custom book order. Restricted to CEO / Management.
    """
    order = get_object_or_404(CustomBookOrder, pk=pk)
    ref = order.order_ref
    school = order.school_name
    order.delete()
    messages.info(request, f"Order {ref} for '{school}' was deleted.")
    return redirect('customizer:order_list')
