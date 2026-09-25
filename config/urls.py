from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.static import serve

# Branded Django Admin Portal Titles
admin.site.site_header = "NAITO DE SAINT ENTERPRISE — Administration"
admin.site.site_title = "Desaint Stationeries Admin Portal"
admin.site.index_title = "Commercial Operations & Managerial ERP"

urlpatterns = [
    # ─── Django Raw Database Admin ────────────────────────────────────────
    path('django-admin/', admin.site.urls),
    path('admin/django/', RedirectView.as_view(url='/django-admin/', permanent=False)),

    # ─── Staff Management Portal (Unified /admin/ prefix) ─────────────────
    # Auth endpoints (login / logout)
    path('admin/', include('managerial.urls', namespace='managerial')),
    path('admin/pos/', include('orders.urls', namespace='orders')),
    path('admin/inventory/', include('inventory.urls', namespace='inventory')),
    path('admin/catalog/', include('catalog.urls', namespace='catalog')),
    path('admin/customizer/', include('customizer.urls', namespace='customizer')),
    path('admin/invoices/', include('invoices.urls', namespace='invoices')),

    # ─── Compatibility redirects from old URL prefixes ─────────────────────
    path('managerial/', RedirectView.as_view(url='/admin/', permanent=False)),
    path('orders/pos/', RedirectView.as_view(url='/admin/pos/pos/', permanent=False)),
    path('customizer/', RedirectView.as_view(url='/admin/customizer/', permanent=False)),
    path('invoices/', RedirectView.as_view(url='/admin/invoices/', permanent=False)),

    # ─── Public Storefront Routes ──────────────────────────────────────────
    # Cart & checkout remain public (B2C customer-facing)
    path('orders/', include('orders.public_urls', namespace='orders_public')),
    path('', include('core.urls')),

    # ─── Media Files (Product Photos, Proofs, Crests) ──────────────────────
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
