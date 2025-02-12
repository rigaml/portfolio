import os
import django
from dotenv import load_dotenv

def pytest_configure(config):
    """
    Django hook to configure pytest.
    """

    env_path = os.getenv('ENV_PATH', 'env/.env.local')
    load_dotenv(env_path)

    os.environ['DJANGO_SETTINGS_MODULE'] = 'portfolio.settings'
    
    django.setup()