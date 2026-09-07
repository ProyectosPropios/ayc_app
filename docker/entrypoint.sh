#!/bin/sh
set -eu

# El contenedor de despliegue siempre debe usar la configuracion de
# produccion. Esto evita que una variable DJANGO_SETTINGS_MODULE antigua de
# Render seleccione accidentalmente settingsDev.py.
export DJANGO_SETTINGS_MODULE=ayc_api.settings

python -c 'import os; from urllib.parse import urlsplit; from django.conf import settings; db = settings.DATABASES.get("default", {}); url = os.environ.get("DATABASE_URL", ""); print("Startup config: settings=%s db_url_present=%s db_url_scheme=%s db_engine=%s" % (os.environ.get("DJANGO_SETTINGS_MODULE"), bool(url.strip()), urlsplit(url).scheme or "missing", db.get("ENGINE", "missing")), flush=True)'

if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
    python manage.py migrate --noinput --settings=ayc_api.settings
    python manage.py collectstatic --noinput --settings=ayc_api.settings
fi

exec "$@"
