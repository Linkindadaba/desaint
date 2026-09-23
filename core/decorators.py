"""
core/decorators.py — Desaint Stationeries RBAC View Decorators
Guards for each staff role, redirecting to /admin/login/ when unauthenticated.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .roles import is_ceo, is_cashier, is_graphics, is_logistics, get_user_role


def staff_required(view_func):
    """Base guard: user must be authenticated staff or superuser."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"/admin/login/?next={request.path}")
        if not (request.user.is_staff or request.user.is_superuser):
            messages.warning(
                request,
                f"Staff credentials required. You are signed in as '{request.user.username}' (customer account)."
            )
            return redirect(f"/admin/login/?next={request.path}")
        return view_func(request, *args, **kwargs)
    return _wrapped


def ceo_required(view_func):
    """Restricts access to CEO group and superusers only."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"/admin/login/?next={request.path}")
        if not is_ceo(request.user):
            messages.error(
                request,
                f"Access Restricted: CEO / Executive privileges required. "
                f"Your role: '{get_user_role(request.user)}'."
            )
            return redirect('managerial:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped


def cashier_required(view_func):
    """Restricts access to Cashier role (and CEO)."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"/admin/login/?next={request.path}")
        if not is_cashier(request.user):
            messages.error(
                request,
                f"Access Restricted: Cashier / POS privileges required. "
                f"Your role: '{get_user_role(request.user)}'."
            )
            return redirect('managerial:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped


def graphics_required(view_func):
    """Restricts access to Graphics Manager role (and CEO)."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"/admin/login/?next={request.path}")
        if not is_graphics(request.user):
            messages.error(
                request,
                f"Access Restricted: Graphics / Proofing privileges required. "
                f"Your role: '{get_user_role(request.user)}'."
            )
            return redirect('managerial:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped


def logistics_required(view_func):
    """Restricts access to Logistics Officer role (and CEO)."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"/admin/login/?next={request.path}")
        if not is_logistics(request.user):
            messages.error(
                request,
                f"Access Restricted: Logistics / Dispatch privileges required. "
                f"Your role: '{get_user_role(request.user)}'."
            )
            return redirect('managerial:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped
