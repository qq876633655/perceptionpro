from rest_framework.routers import DefaultRouter
from django.urls import path
from apps.sim_test_agv import views

router = DefaultRouter()
router.register('at_case_map',        views.CaseMapViewSet,               basename='at_case_map')
router.register('at_case_property', views.CasePropertyViewSet, basename='at_case_property')
router.register('at_common_parameter', views.SchemeCommonParameterViewSet, basename='at_common_parameter')
router.register('at_case_template', views.CaseTemplateViewSet, basename='at_case_template')
router.register('at_test_task', views.AgvTestTaskViewSet, basename='at_test_task')
router.register('at_worker_node', views.WorkerNodeViewSet, basename='at_worker_node')

urlpatterns = router.urls + [
    path('at_worker_status/', views.WorkerStatusView.as_view(), name='at_worker_status'),
]
