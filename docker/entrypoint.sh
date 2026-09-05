#!/bin/sh
set -eu

# El contenedor de despliegue siempre debe usar la configuracion de
# produccion. Esto evita que una variable DJANGO_SETTINGS_MODULE antigua de
# Render seleccione accidentalmente settingsDev.py.
export DJANGO_SETTINGS_MODULE=ayc_api.settings

if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
    python manage.py migrate --noinput --settings=ayc_api.settings
    python manage.py collectstatic --noinput --settings=ayc_api.settings
fi

exec "$@"
