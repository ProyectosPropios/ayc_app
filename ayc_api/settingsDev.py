from .settings import *

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    'default': dj_database_url.config(
        default=env('URL_DB', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}')
    )
}

CORS_ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
CSRF_TRUSTED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
