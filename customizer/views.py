from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from decimal import Decimal
import uuid
from .models import RulingOption, CustomBookOrder
from core.decorators import graphics_required

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

