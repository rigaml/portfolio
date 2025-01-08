import os
import sys
import django
from pathlib import Path
from dotenv import load_dotenv

def pytest_configure(config):
    """
    Django hook to configure pytest.
    """

    project_root = Path(__file__).resolve().parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    env_path = os.getenv('ENV_PATH', project_root / 'env/.env.local')
    load_dotenv(env_path)

    print(f"Hello somebody there: {os.environ}")
    
    os.environ['DJANGO_SETTINGS_MODULE'] = 'portfolio.settings'
    
    django.setup()