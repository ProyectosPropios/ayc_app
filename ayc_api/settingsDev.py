from . import settings as base_settings

# Reutiliza la configuración común sin importar símbolos con wildcard.
for _setting_name in dir(base_settings):
    if _setting_name.isupper():
        globals()[_setting_name] = getattr(base_settings, _setting_name)

BASE_DIR = base_settings.BASE_DIR
env = base_settings.env
dj_database_url = base_settings.dj_database_url

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    'default': dj_database_url.config(
        default=env('URL_DB', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}')
    )
}

CORS_ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
CSRF_TRUSTED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
