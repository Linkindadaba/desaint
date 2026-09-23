from django.shortcuts import render, redirect
from django.contrib import messages
from catalog.models import Product, Category

def home(request):
    """
    Storefront Landing Page for Desaint Stationeries (Naito De Saint Enterprise).
    Features distinctive educational supply branding, 5k-10k custom book highlights,
    corporate citations, and 2-column mobile catalog.
    """
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.filter(is_active=True)

    # Core corporate highlights
    citations_data = [
        {
            'title': 'Registered Enterprise Entity',
            'badge': 'Official Registration',
            'desc': 'Naito De Saint Enterprise — fully incorporated under the laws of Ghana, operating commercial educational printing in Sunyani, Bono Region.',
            'icon': 'fas fa-landmark',
            'color': 'primary',
        },
        {
            'title': 'Statutory GRA Tax Compliance',
            'badge': 'Act 896 (3% WHT)',
            'desc': 'Qualified for high-ticket public and private school tenders with official 3% Withholding Tax deduction proformas and official receipting.',
            'icon': 'fas fa-file-shield',
            'color': 'danger',
        },
        {
            'title': 'Zero-Misprint Digital Proofing',
            'badge': 'Signed Guarantee',
            'desc': 'Digital artwork proof signed off by school proprietors and headmasters prior to plate making, ensuring 100% crest and anthem fidelity.',
            'icon': 'fas fa-file-signature',
            'color': 'success',
        },
        {
            'title': 'Inter-Regional Bus Logistics',
            'badge': '8 Regions Served',
            'desc': 'Same-day and next-day bus parcel delivery via VIP Jeoun, OA Travel, and Imperial Express to terminals across Ghana.',
            'icon': 'fas fa-truck-fast',
            'color': 'info',
        },
    ]

    context = {
        'products': products,
        'categories': categories,
        'citations_data': citations_data,
        'active_nav': 'home',
    }
    return render(request, 'core/home.html', context)


def about(request):
    """
    About Us Page — The Story, Mission, and Executive Leadership of Desaint Stationeries.
    """
    return render(request, 'core/about.html', {
        'active_nav': 'about',
    })


def citations(request):
    """
    Citations, Accreditations & Institutional Trust Page.
    Details legal incorporation, GRA tax compliance, quality benchmarks, and school testimonials.
    """
    return render(request, 'core/citations.html', {
        'active_nav': 'citations',
    })


def contact(request):
    """
    Contact Us Page — Head office contacts, regional dispatch hubs, and inquiry form.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        institution = request.POST.get('institution', '').strip()
        message = request.POST.get('message', '').strip()

        if name and phone:
            messages.success(
                request,
                f"Thank you, {name}! Your message regarding '{institution or 'Educational Supplies'}' has been received. Our Sunyani dispatch team will reach out to you shortly via {phone}."
            )
            return redirect('core:contact')
        else:
            messages.error(request, "Please provide your name and an active phone number.")

    return render(request, 'core/contact.html', {
        'active_nav': 'contact',
    })

