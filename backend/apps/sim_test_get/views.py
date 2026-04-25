from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from apps.back_stage.permissions import HasModelPermission
from apps.common_views.views import BaseModelViewSet
from apps.sim_test_get.models import GetTestTarget, AgvBody, GetTestCommonParameter
from apps.sim_test_get.serializers import (
    GetTestTargetSerializer, AgvBodySerializer, GetTestCommonParameterSerializer,
)
from apps.sim_test_get.filters import (
    GetTestTargetFilter, AgvBodyFilter, GetTestCommonParameterFilter,
)

User = get_user_model()

_PERMS = [IsAuthenticated, HasModelPermission]
_FILTER_BACKENDS = [DjangoFilterBackend, SearchFilter, OrderingFilter]


# ── GetTestTarget ────────────────────────────────────────────────────

class GetTestTargetViewSet(BaseModelViewSet):
    queryset = GetTestTarget.objects.all().order_by('-create_time')
    serializer_class = GetTestTargetSerializer
    permission_classes = _PERMS
    filter_backends = _FILTER_BACKENDS
    filterset_class = GetTestTargetFilter
    search_fields = ['target_name', 'model_name']
    ordering_fields = ['create_time']

    @action(methods=['post'], detail=False)
    def batch_delete(self, request):
        GetTestTarget.objects.filter(id__in=request.data.get('ids', [])).delete()
        return Response({'msg': '删除成功'})

    @action(methods=['get'], detail=False)
    def creators(self, request):
        ids = GetTestTarget.objects.exclude(created_by=None).values_list('created_by', flat=True).distinct()
        return Response(list(User.objects.filter(id__in=ids).values('id', 'username')))


# ── AgvBody ──────────────────────────────────────────────────────────

class AgvBodyViewSet(BaseModelViewSet):
    queryset = AgvBody.objects.all().order_by('-create_time')
    serializer_class = AgvBodySerializer
    permission_classes = _PERMS
    filter_backends = _FILTER_BACKENDS
    filterset_class = AgvBodyFilter
    search_fields = ['agv_type']
    ordering_fields = ['create_time']

    @action(methods=['post'], detail=False)
    def batch_delete(self, request):
        AgvBody.objects.filter(id__in=request.data.get('ids', [])).delete()
        return Response({'msg': '删除成功'})

    @action(methods=['get'], detail=False)
    def creators(self, request):
        ids = AgvBody.objects.exclude(created_by=None).values_list('created_by', flat=True).distinct()
        return Response(list(User.objects.filter(id__in=ids).values('id', 'username')))


# ── GetTestCommonParameter ───────────────────────────────────────────

class GetTestCommonParameterViewSet(BaseModelViewSet):
    queryset = GetTestCommonParameter.objects.all().order_by('-create_time')
    serializer_class = GetTestCommonParameterSerializer
    permission_classes = _PERMS
    filter_backends = _FILTER_BACKENDS
    filterset_class = GetTestCommonParameterFilter
    search_fields = ['common_parameter_name']
    ordering_fields = ['create_time']

    @action(methods=['post'], detail=False)
    def batch_delete(self, request):
        GetTestCommonParameter.objects.filter(id__in=request.data.get('ids', [])).delete()
        return Response({'msg': '删除成功'})

    @action(methods=['get'], detail=False)
    def creators(self, request):
        ids = GetTestCommonParameter.objects.exclude(created_by=None).values_list('created_by', flat=True).distinct()
        return Response(list(User.objects.filter(id__in=ids).values('id', 'username')))

    @action(methods=['get'], detail=False, url_path='choices')
    def choices(self, request):
        def distinct_values(field):
            return list(
                GetTestCommonParameter.objects.exclude(**{field: ''})
                .values_list(field, flat=True).distinct().order_by(field)
            )
        return Response({
            'sim_test_version': distinct_values('sim_test_version'),
            'sim_test_vehicle': distinct_values('sim_test_vehicle'),
        })
