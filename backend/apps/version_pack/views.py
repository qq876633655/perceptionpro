from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from apps.back_stage.permissions import HasModelPermission

from apps.version_pack.models import PerEnv, PerVersion, LocEnv, LocVersion, CtlEnv, CtlVersion, SimEnv, SimVersion, SenEnv, SenVersion, AtEnv, AtVersion
from apps.version_pack.serializers import (
    PerEnvSerializer, PerVersionCreateSerializer, PerVersionUpdateSerializer, PerVersionListSerializer,
    LocEnvSerializer, LocVersionCreateSerializer, LocVersionUpdateSerializer, LocVersionListSerializer,
    CtlEnvSerializer, CtlVersionCreateSerializer, CtlVersionUpdateSerializer, CtlVersionListSerializer,
    SimEnvSerializer, SimVersionCreateSerializer, SimVersionUpdateSerializer, SimVersionListSerializer,
    SenEnvSerializer, SenVersionCreateSerializer, SenVersionUpdateSerializer, SenVersionListSerializer,
    AtEnvSerializer, AtVersionCreateSerializer, AtVersionUpdateSerializer, AtVersionListSerializer,
)
from apps.version_pack.filters import (
    PerEnvFilter, PerVersionFilter,
    LocEnvFilter, LocVersionFilter,
    CtlEnvFilter, CtlVersionFilter,
    SimEnvFilter, SimVersionFilter,
    SenEnvFilter, SenVersionFilter,
    AtEnvFilter, AtVersionFilter,
)
from rest_framework.response import Response
from apps.common_views.views import BaseModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
import threading
from common.dd_robot import per_version_release_dd, loc_version_release_dd, ctl_version_release_dd

User = get_user_model()

_COMMON_PERMISSIONS = [IsAuthenticated, HasModelPermission]
_FILTER_BACKENDS    = [DjangoFilterBackend, SearchFilter, OrderingFilter]


# ════════════════════════════════════════════════════════════════════
# 通用 ViewSet 工厂
# ════════════════════════════════════════════════════════════════════

def make_env_viewset(env_model, env_serializer, env_filter, search_fields=None):
    _search_fields = search_fields or ['env_name']
    class _EnvViewSet(BaseModelViewSet):
        queryset = env_model.objects.all().order_by('-create_time')
        serializer_class = env_serializer
        permission_classes = _COMMON_PERMISSIONS
        filter_backends = _FILTER_BACKENDS
        filterset_class = env_filter
        ordering_fields = ['create_time']
        search_fields = _search_fields

        @action(methods=['get'], detail=False)
        def creators(self, request):
            user_ids = env_model.objects.exclude(created_by=None).values_list('created_by', flat=True).distinct()
            users = User.objects.filter(id__in=user_ids).values('id', 'username')
            return Response(list(users))

    _EnvViewSet.__name__ = f'{env_model.__name__}ViewSet'
    return _EnvViewSet


def make_version_viewset(ver_model, create_ser, update_ser, list_ser, ver_filter, search_fields=None, notify_fn=None):
    _search_fields = search_fields or ['version_num']
    class _VersionViewSet(BaseModelViewSet):
        queryset = ver_model.objects.all().order_by('-create_time')
        permission_classes = _COMMON_PERMISSIONS
        filter_backends = _FILTER_BACKENDS
        filterset_class = ver_filter
        ordering_fields = ['create_time']
        search_fields = _search_fields

        def get_serializer_class(self):
            if self.action == 'create':
                return create_ser
            if self.action in ['update', 'partial_update']:
                return update_ser
            return list_ser

        def perform_create(self, serializer):
            super().perform_create(serializer)
            if notify_fn:
                instance = serializer.instance
                threading.Thread(
                    target=notify_fn, args=(instance,), daemon=True
                ).start()

        @action(methods=['get'], detail=False)
        def creators(self, request):
            user_ids = ver_model.objects.exclude(created_by=None).values_list('created_by', flat=True).distinct()
            users = User.objects.filter(id__in=user_ids).values('id', 'username')
            return Response(list(users))

    _VersionViewSet.__name__ = f'{ver_model.__name__}ViewSet'
    return _VersionViewSet


# ════════════════════════════════════════════════════════════════════
# Per / Loc / Ctl / Sim / Sen / At（工厂生成）
# ════════════════════════════════════════════════════════════════════

PerEnvViewSet     = make_env_viewset(PerEnv, PerEnvSerializer, PerEnvFilter)
PerVersionViewSet = make_version_viewset(PerVersion, PerVersionCreateSerializer, PerVersionUpdateSerializer, PerVersionListSerializer, PerVersionFilter, notify_fn=per_version_release_dd)

LocEnvViewSet     = make_env_viewset(LocEnv, LocEnvSerializer, LocEnvFilter)
LocVersionViewSet = make_version_viewset(LocVersion, LocVersionCreateSerializer, LocVersionUpdateSerializer, LocVersionListSerializer, LocVersionFilter, notify_fn=loc_version_release_dd)

CtlEnvViewSet     = make_env_viewset(CtlEnv, CtlEnvSerializer, CtlEnvFilter)
CtlVersionViewSet = make_version_viewset(CtlVersion, CtlVersionCreateSerializer, CtlVersionUpdateSerializer, CtlVersionListSerializer, CtlVersionFilter, notify_fn=ctl_version_release_dd)

SimEnvViewSet     = make_env_viewset(SimEnv, SimEnvSerializer, SimEnvFilter)
SimVersionViewSet = make_version_viewset(SimVersion, SimVersionCreateSerializer, SimVersionUpdateSerializer, SimVersionListSerializer, SimVersionFilter)

SenEnvViewSet     = make_env_viewset(SenEnv, SenEnvSerializer, SenEnvFilter)
SenVersionViewSet = make_version_viewset(SenVersion, SenVersionCreateSerializer, SenVersionUpdateSerializer, SenVersionListSerializer, SenVersionFilter)

AtEnvViewSet     = make_env_viewset(AtEnv, AtEnvSerializer, AtEnvFilter)
AtVersionViewSet = make_version_viewset(AtVersion, AtVersionCreateSerializer, AtVersionUpdateSerializer, AtVersionListSerializer, AtVersionFilter)
