import os

from celery import Celery

os.environ["DJANGO_SETTINGS_MODULE"] = "ayc_api.settings"

app = Celery("ayc_api")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
