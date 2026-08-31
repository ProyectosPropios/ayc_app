"""
URL configuration for ayc_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.db import connection
from django.db.utils import OperationalError
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    """Endpoint used by Render to verify that the API and database are ready."""
    try:
        connection.ensure_connection()
    except OperationalError:
        return JsonResponse({'status': 'error', 'database': 'unavailable'}, status=503)
    return JsonResponse({'status': 'ok'})


urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/customers/', include('customer.urls')),
    path('api/work-orders/', include('workorder.urls')),
    path('api/notifications/', include('notification.urls')),
    path('api/electrical-reports/', include('electricalreport.urls')),
    path('api/pumping-reports/', include('pumpingreport.urls')),
]
