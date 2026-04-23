from rest_framework.routers import DefaultRouter
from apps.version_pack.views import (
    PerEnvViewSet, PerVersionViewSet,
    LocEnvViewSet, LocVersionViewSet,
    CtlEnvViewSet, CtlVersionViewSet,
    SimEnvViewSet, SimVersionViewSet,
    SenEnvViewSet, SenVersionViewSet,
)

router = DefaultRouter()
router.register('per_env',     PerEnvViewSet)
router.register('per_version', PerVersionViewSet)
router.register('loc_env',     LocEnvViewSet)
router.register('loc_version', LocVersionViewSet)
router.register('ctl_env',     CtlEnvViewSet)
router.register('ctl_version', CtlVersionViewSet)
router.register('sim_env',     SimEnvViewSet)
router.register('sim_version', SimVersionViewSet)
router.register('sen_env',     SenEnvViewSet)
router.register('sen_version', SenVersionViewSet)

urlpatterns = router.urls