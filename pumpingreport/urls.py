from rest_framework.routers import DefaultRouter

from .views import PumpingReportViewSet


router = DefaultRouter()
router.register("", PumpingReportViewSet, basename="pumping-report")

urlpatterns = router.urls
