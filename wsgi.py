"""
WSGI config for Vercel and WSGI runners.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from api.index import app as application, app

__all__ = ['application', 'app']
