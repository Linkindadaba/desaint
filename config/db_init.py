import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def initialize_database():
    if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        tmp_db = Path('/tmp/db.sqlite3')
        if not tmp_db.exists():
            src_db = BASE_DIR / 'db.sqlite3'
            if src_db.exists():
                try:
                    shutil.copyfile(src_db, tmp_db)
                    return
                except Exception as e:
                    print(f"Notice: Copy db failed: {e}")

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
