from rest_framework.routers import DefaultRouter
from apps.data_manage.views import SimProjectPropertyViewSet, SimCommonPropertyViewSet

router = DefaultRouter()
router.register('sim_project_property', SimProjectPropertyViewSet)
router.register('sim_common_property', SimCommonPropertyViewSet)

urlpatterns = router.urls
