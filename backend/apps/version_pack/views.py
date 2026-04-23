from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from apps.back_stage.permissions import HasModelPermission

from apps.version_pack.models import PerEnv, PerVersion, LocEnv, LocVersion, CtlEnv, CtlVersion, SimEnv, SimVersion, SenEnv, SenVersion
from apps.version_pack.serializers import (
    PerEnvSerializer, PerVersionCreateSerializer, PerVersionUpdateSerializer, PerVersionListSerializer,
    LocEnvSerializer, LocVersionCreateSerializer, LocVersionUpdateSerializer, LocVersionListSerializer,
    CtlEnvSerializer, CtlVersionCreateSerializer, CtlVersionUpdateSerializer, CtlVersionListSerializer,
    SimEnvSerializer, SimVersionCreateSerializer, SimVersionUpdateSerializer, SimVersionListSerializer,
    SenEnvSerializer, SenVersionCreateSerializer, SenVersionUpdateSerializer, SenVersionListSerializer,
)
from apps.version_pack.filters import (
    PerEnvFilter, PerVersionFilter,
    LocEnvFilter, LocVersionFilter,
    CtlEnvFilter, CtlVersionFilter,
    SimEnvFilter, SimVersionFilter,
    SenEnvFilter, SenVersionFilter,
)
from rest_framework.response import Response
from apps.common_views.views import BaseModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

User = get_user_model()

_COMMON_PERMISSIONS = [IsAuthenticated, HasModelPermission]
_FILTER_BACKENDS    = [DjangoFilterBackend, SearchFilter, OrderingFilter]


# ════════════════════════════════════════════════════════════════════
# 通用 ViewSet 工厂
# ════════════════════════════════════════════════════════════════════

def make_env_viewset(env_model, env_serializer, env_filter, search_fields=None):
    class _EnvViewSet(BaseModelViewSet):
        queryset = env_model.objects.all().order_by('-create_time')
        serializer_class = env_serializer
        permission_classes = _COMMON_PERMISSIONS
        filter_backends = _FILTER_BACKENDS
        filterset_class = env_filter
        ordering_fields = ['create_time']

        def get_search_fields(self):
            return search_fields or ['env_name']

        @action(methods=['post'], detail=False)
        def batch_delete(self, request):
            ids = request.data.get("ids", [])
            env_model.objects.filter(id__in=ids).delete()
            return Response({"msg": "删除成功"})

        @action(methods=['get'], detail=False)
        def creators(self, request):
            user_ids = env_model.objects.exclude(created_by=None).values_list('created_by', flat=True).distinct()
            users = User.objects.filter(id__in=user_ids).values('id', 'username')
            return Response(list(users))

    _EnvViewSet.__name__ = f'{env_model.__name__}ViewSet'
    return _EnvViewSet


def make_version_viewset(ver_model, env_model, create_ser, update_ser, list_ser, ver_filter, search_fields=None):
    class _VersionViewSet(BaseModelViewSet):
        queryset = ver_model.objects.all().order_by('-create_time')
        permission_classes = _COMMON_PERMISSIONS
        filter_backends = _FILTER_BACKENDS
        filterset_class = ver_filter
        ordering_fields = ['create_time']

        def get_search_fields(self):
            return search_fields or ['version_num']

        def get_serializer_class(self):
            if self.action == 'create':
                return create_ser
            if self.action in ['update', 'partial_update']:
                return update_ser
            return list_ser

        @action(methods=['post'], detail=False)
        def batch_delete(self, request):
            ids = request.data.get("ids", [])
            ver_model.objects.filter(id__in=ids).delete()
            return Response({"msg": "删除成功"})

        @action(methods=['get'], detail=False)
        def creators(self, request):
            user_ids = ver_model.objects.exclude(created_by=None).values_list('created_by', flat=True).distinct()
            users = User.objects.filter(id__in=user_ids).values('id', 'username')
            return Response(list(users))

    _VersionViewSet.__name__ = f'{ver_model.__name__}ViewSet'
    return _VersionViewSet


# ════════════════════════════════════════════════════════════════════
# Per（感知）
# ════════════════════════════════════════════════════════════════════

class PerEnvViewSet(BaseModelViewSet):
    queryset = PerEnv.objects.all().order_by('-create_time')
    serializer_class = PerEnvSerializer
    permission_classes = _COMMON_PERMISSIONS
    filter_backends = _FILTER_BACKENDS
    filterset_class = PerEnvFilter
    search_fields = ['env_name']
    ordering_fields = ['create_time']

    @action(methods=['post'], detail=False)
    def batch_delete(self, request):
        ids = request.data.get("ids", [])
        PerEnv.objects.filter(id__in=ids).delete()
        return Response({"msg": "删除成功"})

    @action(methods=['get'], detail=False)
    def creators(self, request):
        user_ids = PerEnv.objects.exclude(created_by=None).values_list('created_by', flat=True).distinct()
        users = User.objects.filter(id__in=user_ids).values('id', 'username')
        return Response(list(users))


class PerVersionViewSet(BaseModelViewSet):
    queryset = PerVersion.objects.all().order_by('-create_time')
    permission_classes = _COMMON_PERMISSIONS
    filter_backends = _FILTER_BACKENDS
    filterset_class = PerVersionFilter
    search_fields = ['version_num']
    ordering_fields = ['create_time']

    def get_serializer_class(self):
        if self.action == 'create':
            return PerVersionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PerVersionUpdateSerializer
        return PerVersionListSerializer

    @action(methods=['post'], detail=False)
    def batch_delete(self, request):
        ids = request.data.get("ids", [])
        PerVersion.objects.filter(id__in=ids).delete()
        return Response({"msg": "删除成功"})

    @action(methods=['get'], detail=False)
    def creators(self, request):
        user_ids = PerVersion.objects.exclude(created_by=None).values_list('created_by', flat=True).distinct()
        users = User.objects.filter(id__in=user_ids).values('id', 'username')
        return Response(list(users))


# ════════════════════════════════════════════════════════════════════
# Loc / Ctl / Sim / Sen（工厂生成）
# ════════════════════════════════════════════════════════════════════

LocEnvViewSet     = make_env_viewset(LocEnv, LocEnvSerializer, LocEnvFilter)
LocVersionViewSet = make_version_viewset(LocVersion, LocEnv, LocVersionCreateSerializer, LocVersionUpdateSerializer, LocVersionListSerializer, LocVersionFilter)

CtlEnvViewSet     = make_env_viewset(CtlEnv, CtlEnvSerializer, CtlEnvFilter)
CtlVersionViewSet = make_version_viewset(CtlVersion, CtlEnv, CtlVersionCreateSerializer, CtlVersionUpdateSerializer, CtlVersionListSerializer, CtlVersionFilter)

SimEnvViewSet     = make_env_viewset(SimEnv, SimEnvSerializer, SimEnvFilter)
SimVersionViewSet = make_version_viewset(SimVersion, SimEnv, SimVersionCreateSerializer, SimVersionUpdateSerializer, SimVersionListSerializer, SimVersionFilter)

SenEnvViewSet     = make_env_viewset(SenEnv, SenEnvSerializer, SenEnvFilter)
SenVersionViewSet = make_version_viewset(SenVersion, SenEnv, SenVersionCreateSerializer, SenVersionUpdateSerializer, SenVersionListSerializer, SenVersionFilter)
