from .base import *

# Override DEBUG if needed (though it's read from .env in base.py)
DEBUG = env.bool('DEBUG', default=True)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
