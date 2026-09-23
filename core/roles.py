"""
core/roles.py — Desaint Stationeries RBAC Role Engine
Mirrors the Cotakyi `core/roles.py` pattern, adapted for Desaint's 4-role staff structure.
Roles defined in startup_team_work_distribution.md:
  - CEO (Founder & CEO — full access)
  - Cashier (Counter POS operator)
  - Graphics (School customizer, artwork proofing)
  - Logistics (Regional waybill & dispatch)
"""
from django.contrib.auth.models import Group

ROLE_CEO = 'CEO'
ROLE_CASHIER = 'Cashier'
ROLE_GRAPHICS = 'Graphics'
ROLE_LOGISTICS = 'Logistics'

ALL_ROLES = [ROLE_CEO, ROLE_CASHIER, ROLE_GRAPHICS, ROLE_LOGISTICS]


def setup_roles():
    """Ensure the 4 standard Desaint RBAC groups exist in the database."""
    for role in ALL_ROLES:
        Group.objects.get_or_create(name=role)


def get_user_role(user):
    """Returns a human-readable primary role label for template display."""
    if not user or not user.is_authenticated:
        return 'Guest'
    if user.is_superuser:
        return 'CEO / Superuser'
    for role in [ROLE_CEO, ROLE_CASHIER, ROLE_GRAPHICS, ROLE_LOGISTICS]:
        if user.groups.filter(name=role).exists():
            return role
    if user.is_staff:
        return 'Staff'
    return 'Customer'


def is_ceo(user):
    """CEO or superuser — full access to all management sections."""
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name=ROLE_CEO).exists()
    )


def is_cashier(user):
    """Cashier POS operator — CEO also has cashier access."""
    return user.is_authenticated and (
        user.is_superuser or
        user.groups.filter(name__in=[ROLE_CEO, ROLE_CASHIER]).exists()
    )


def is_graphics(user):
    """Graphics Manager — CEO also has graphics access."""
    return user.is_authenticated and (
        user.is_superuser or
        user.groups.filter(name__in=[ROLE_CEO, ROLE_GRAPHICS]).exists()
    )


def is_logistics(user):
    """Logistics Officer — CEO also has logistics access."""
    return user.is_authenticated and (
        user.is_superuser or
        user.groups.filter(name__in=[ROLE_CEO, ROLE_LOGISTICS]).exists()
    )


def is_any_staff(user):
    """Returns True if user is authenticated staff member of any role."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)
