from rest_framework.routers import DefaultRouter
from apps.sim_test_get import views

router = DefaultRouter()
router.register('gt_test_target', views.GetTestTargetViewSet, basename='gt_test_target')
router.register('gt_agv_body', views.AgvBodyViewSet, basename='gt_agv_body')
router.register('gt_common_param', views.GetTestCommonParameterViewSet, basename='gt_common_param')

urlpatterns = router.urls
