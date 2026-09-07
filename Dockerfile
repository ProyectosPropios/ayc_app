FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=10000

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        fonts-dejavu \
        libffi8 \
        libgdk-pixbuf-2.0-0 \
        libharfbuzz-subset0 \
        libharfbuzz0b \
        libjpeg62-turbo \
        libopenjp2-7 \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.lock .
RUN python -m pip install --no-cache-dir -r requirements.lock

COPY manage.py ./
COPY ayc_api ./ayc_api
COPY core ./core
COPY customer ./customer
COPY electricalreport ./electricalreport
COPY generalreport ./generalreport
COPY notification ./notification
COPY pumpingreport ./pumpingreport
COPY users ./users
COPY workorder ./workorder
COPY docker/entrypoint.sh /entrypoint.sh

# Los archivos estaticos quedan dentro de la imagen para que Render los sirva
# tambien en los procesos que no tienen un volumen compartido.
RUN python manage.py collectstatic --noinput --settings=ayc_api.settings \
    && addgroup --system app \
    && adduser --system --ingroup app app \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R app:app /app /entrypoint.sh \
    && chmod +x /entrypoint.sh

USER app

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["sh", "-c", "exec gunicorn --env DJANGO_SETTINGS_MODULE=ayc_api.settings ayc_api.wsgi:application --bind 0.0.0.0:${PORT:-10000} --workers 3 --timeout 120"]
