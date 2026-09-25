import os
import shutil
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def is_db_valid(db_path: Path) -> bool:
    """Check if SQLite database exists and has essential tables."""
    if not db_path.exists() or db_path.stat().st_size < 10000:
        return False
    try:
        conn = sqlite3.connect(str(db_path), timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='catalog_product';")
        has_table = cursor.fetchone() is not None
        conn.close()
        return has_table
    except Exception:
        return False

def initialize_database():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # Check if running in Vercel or serverless environment
    is_serverless = bool(
        os.environ.get('VERCEL') or
        os.environ.get('AWS_LAMBDA_FUNCTION_NAME') or
        os.environ.get('VERCEL_ENV') or
        os.environ.get('VERCEL_REGION') or
        os.environ.get('VERCEL_URL')
    )
    
    if is_serverless:
        tmp_db = Path('/tmp/db.sqlite3')
        
        # If /tmp/db.sqlite3 is already valid, do nothing
        if is_db_valid(tmp_db):
            return

        # 1. Search for pre-seeded database file across common paths
        candidate_paths = [
            BASE_DIR / 'db.sqlite3',
            Path('/var/task/db.sqlite3'),
            Path.cwd() / 'db.sqlite3',
            Path(__file__).resolve().parent.parent / 'db.sqlite3',
        ]
        
        for candidate in candidate_paths:
            if candidate.exists() and is_db_valid(candidate):
                try:
                    tmp_db.parent.mkdir(parents=True, exist_ok=True)
                    if tmp_db.exists():
                        try:
                            tmp_db.unlink()
                        except Exception:
                            pass
                    shutil.copyfile(candidate, tmp_db)
                    print(f"Initialized /tmp/db.sqlite3 from {candidate}")
                    return
                except Exception as e:
                    print(f"Notice: Copy db from {candidate} failed: {e}")

        # 2. Fallback: Run migrations and seed data programmatically
        try:
            import django
            django.setup()
            from django.core.management import call_command
            call_command('migrate', interactive=False, verbosity=0)
            try:
                import seed_initial_data
                seed_initial_data.seed_data()
            except Exception as se:
                print(f"Seed note: {se}")
        except Exception as me:
            print(f"Migrate note: {me}")
