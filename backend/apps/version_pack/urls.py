# apps/version_pack/urls/perception.py

from rest_framework.routers import DefaultRouter
from apps.version_pack.views import (
    PerEnvViewSet,
    PerVersionViewSet
)

router = DefaultRouter()
router.register('per_env', PerEnvViewSet)
router.register('per_version', PerVersionViewSet)

urlpatterns = router.urls