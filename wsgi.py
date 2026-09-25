"""
WSGI config for Vercel and WSGI runners.
"""
from api.index import app as application, app

__all__ = ['application', 'app']
