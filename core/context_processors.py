from .roles import is_ceo, is_cashier, is_graphics, is_logistics, get_user_role


def company_context(request):
    """Global branding + role context for all templates (storefront & admin)."""
    ctx = {
        'COMPANY_NAME': 'Naito De Saint Enterprise',
        'BRAND_NAME': 'Desaint Stationeries',
        'BRAND_MOTTO': 'Quality You See and Trust',
        'BRAND_SLOGAN': 'Write. Create. Inspire.',
        'HEAD_OFFICE': 'Sunyani, Bono Region, Ghana',
        'PHONE_PRIMARY': '+233 20 015 2394',
        'PHONE_SECONDARY': '+233 24 606 5822',
        'EMAIL_OFFICIAL': 'info@desaintstationeries.com',
        'EMAIL_SALES': 'sales@desaintstationeries.com',
        'CURRENCY_SYMBOL': 'GH₵',
        'LOGO_URL': '/static/img/logo.jpeg',
        'MEDIA_LOGO_URL': '/media/logo/logo.jpeg',
        # Role flags (always present, False for anonymous / customers)
        'is_ceo': False,
        'is_cashier': False,
        'is_graphics': False,
        'is_logistics': False,
        'user_role': 'Guest',
        # Sidebar badge counts
        'pending_proofs_count': 0,
        'waybills_in_transit_count': 0,
        'overdue_credit_count': 0,
    }

    user = getattr(request, 'user', None)
    if user and user.is_authenticated and (user.is_staff or user.is_superuser):
        # Role flags
        ctx['is_ceo'] = is_ceo(user)
        ctx['is_cashier'] = is_cashier(user)
        ctx['is_graphics'] = is_graphics(user)
        ctx['is_logistics'] = is_logistics(user)
        ctx['user_role'] = get_user_role(user)

        # Sidebar badge counts (lazy imports to avoid circular deps)
        try:
            from customizer.models import CustomBookOrder
            ctx['pending_proofs_count'] = CustomBookOrder.objects.filter(
                status='PROOF_PENDING'
            ).count()
        except Exception:
            pass

        try:
            from managerial.models import RegionalWaybill, SchoolCreditRecord
            ctx['waybills_in_transit_count'] = RegionalWaybill.objects.filter(
                status='IN_TRANSIT'
            ).count()
            ctx['overdue_credit_count'] = SchoolCreditRecord.objects.filter(
                status='OVERDUE_NOTICE'
            ).count()
        except Exception:
            pass

    # Cart count for storefront navbar
    try:
        from orders.cart import Cart
        ctx['cart_count'] = len(Cart(request))
    except Exception:
        ctx['cart_count'] = 0

    return ctx
