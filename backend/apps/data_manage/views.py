from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from apps.back_stage.permissions import HasModelPermission
from apps.common_views.views import BaseModelViewSet
from apps.data_manage.models import SimProjectProperty, SimCommonProperty
from apps.data_manage.serializers import SimProjectPropertySerializer, SimCommonPropertySerializer
from apps.data_manage.filters import SimProjectPropertyFilter, SimCommonPropertyFilter

User = get_user_model()

_COMMON_PERMISSIONS = [IsAuthenticated, HasModelPermission]
_FILTER_BACKENDS = [DjangoFilterBackend, SearchFilter, OrderingFilter]


class SimProjectPropertyViewSet(BaseModelViewSet):
    queryset = SimProjectProperty.objects.all().order_by('-create_time')
    serializer_class = SimProjectPropertySerializer
    permission_classes = _COMMON_PERMISSIONS
    filter_backends = _FILTER_BACKENDS
    filterset_class = SimProjectPropertyFilter
    search_fields = ['apply_project']
    ordering_fields = ['create_time']

    @action(methods=['get'], detail=False)
    def creators(self, request):
        user_ids = (
            SimProjectProperty.objects
            .exclude(created_by=None)
            .values_list('created_by', flat=True)
            .distinct()
        )
        users = User.objects.filter(id__in=user_ids).values('id', 'username')
        return Response(list(users))


class SimCommonPropertyViewSet(BaseModelViewSet):
    queryset = SimCommonProperty.objects.all().order_by('-create_time')
    serializer_class = SimCommonPropertySerializer
    permission_classes = _COMMON_PERMISSIONS
    filter_backends = _FILTER_BACKENDS
    filterset_class = SimCommonPropertyFilter
    search_fields = ['versions']
    ordering_fields = ['create_time']

    @action(methods=['get'], detail=False)
    def creators(self, request):
        user_ids = (
            SimCommonProperty.objects
            .exclude(created_by=None)
            .values_list('created_by', flat=True)
            .distinct()
        )
        users = User.objects.filter(id__in=user_ids).values('id', 'username')
        return Response(list(users))
