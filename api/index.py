import os
import sys
from pathlib import Path

# Add repository root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Bootstrap /tmp database if needed
try:
    from config.db_init import initialize_database
    initialize_database()
except Exception as e:
    print(f"DB Init Exception: {e}")

from config.path_utils import normalize_wsgi_path
from django.core.wsgi import get_wsgi_application

_django_application = get_wsgi_application()

def app(environ, start_response):
    """
    WSGI wrapper for Vercel Serverless Function runtime.
    """
    normalize_wsgi_path(environ)
    return _django_application(environ, start_response)

application = app
