from rest_framework.routers import DefaultRouter

from .views import ElectricalReportViewSet


router = DefaultRouter()
router.register("", ElectricalReportViewSet, basename="electrical-report")

urlpatterns = router.urls
