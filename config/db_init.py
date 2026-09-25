import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def initialize_database():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # Check if running in Vercel or serverless environment
    if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME') or os.environ.get('VERCEL_ENV'):
        tmp_db = Path('/tmp/db.sqlite3')
        if not tmp_db.exists():
            # 1. Fast path: Copy pre-seeded SQLite database from package root
            src_db = BASE_DIR / 'db.sqlite3'
            if src_db.exists():
                try:
                    tmp_db.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src_db, tmp_db)
                    print("Initialized /tmp/db.sqlite3 from repository package.")
                    return
                except Exception as e:
                    print(f"Notice: Copy db failed: {e}")

            # 2. Fallback: Run migrations and seed data
            try:
                import django
                django.setup()
                from django.core.management import call_command
                call_command('migrate', interactive=False)
                try:
                    import seed_initial_data
                    seed_initial_data.seed_data()
                except Exception as se:
                    print(f"Seed note: {se}")
            except Exception as me:
                print(f"Migrate note: {me}")
