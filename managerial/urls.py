from django.urls import path
from . import views

app_name = 'managerial'

urlpatterns = [
    # ─── Authentication ────────────────────────────────────────────────────
    path('login/', views.staff_login_view, name='staff_login'),
    path('logout/', views.staff_logout_view, name='staff_logout'),

    # ─── Admin Dashboard (root /admin/ landing) ────────────────────────────
    path('', views.dashboard, name='dashboard'),
    path('analytics/', views.analytics_view, name='analytics'),

    # ─── CEO-Only Sections ─────────────────────────────────────────────────
    path('credit-ledger/', views.credit_ledger, name='credit_ledger'),
    path('credit/payment/', views.record_payment, name='record_payment_general'),
    path('credit/payment/<int:pk>/', views.record_payment, name='record_payment'),

    # ─── Staff Directory & Role Management (CEO Only) ──────────────────────
    path('staff/', views.staff_list_view, name='staff_list'),
    path('staff/add/', views.staff_create_view, name='staff_create'),
    path('staff/<int:pk>/edit/', views.staff_edit_view, name='staff_edit'),

    # ─── Database Backups & Disaster Recovery (CEO Only) ───────────────────
    path('backup/', views.database_backup_view, name='database_backup'),
    path('backup/export/json/', views.export_database_json, name='export_database_json'),
    path('backup/export/sqlite/', views.download_sqlite_backup, name='download_sqlite_backup'),
    path('backup/export/csv/<str:dataset>/', views.export_csv_view, name='export_csv'),
    path('backup/restore/', views.restore_database_json, name='restore_database_json'),

    # ─── Logistics Sections ────────────────────────────────────────────────
    path('waybills/', views.waybills, name='waybills'),
    path('waybills/create/', views.create_waybill, name='create_waybill'),
]
