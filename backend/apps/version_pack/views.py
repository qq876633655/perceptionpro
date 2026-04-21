from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from apps.version_pack.models import PerEnv, PerVersion
from apps.version_pack.serializers import (
    PerEnvSerializer,
    PerVersionCreateSerializer,
    PerVersionUpdateSerializer,
    PerVersionListSerializer
)
from apps.version_pack.filters import PerVersionFilter
from rest_framework.response import Response
from apps.common_views.views import BaseModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser


# ✅ 环境管理
class PerEnvViewSet(BaseModelViewSet):
    queryset = PerEnv.objects.all().order_by('-create_time')
    serializer_class = PerEnvSerializer


# ✅ 版本管理
class PerVersionViewSet(BaseModelViewSet):
    queryset = PerVersion.objects.all().order_by('-create_time')
    filterset_class = PerVersionFilter

    search_fields = ['version_num']
    ordering_fields = ['create_time']

    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == 'create':
            return PerVersionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PerVersionUpdateSerializer
        return PerVersionListSerializer

    # ✅ 批量删除
    @action(methods=['post'], detail=False)
    def batch_delete(self, request):
        ids = request.data.get("ids", [])
        PerVersion.objects.filter(id__in=ids).delete()
        return Response({"msg": "删除成功"})
