import os
from dotenv import load_dotenv

env_path = os.getenv('ENV_PATH', 'env/.env.local')
load_dotenv(env_path)

if 'production' in env_path:
    from .production import *
elif 'development' in env_path:
    from .development import *
else:
    from .local import *