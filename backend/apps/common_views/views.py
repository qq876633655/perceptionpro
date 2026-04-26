import io
import logging
import os
import shutil
import zipfile

from django.conf import settings
from django.http import StreamingHttpResponse
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

audit_log = logging.getLogger('apps.audit')


class BaseModelViewSet(ModelViewSet):
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        instance = serializer.instance
        audit_log.info('新增 %s [pk=%s] by %s', instance._meta.verbose_name, instance.pk, self.request.user.username)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
        instance = serializer.instance
        audit_log.info('修改 %s [pk=%s] by %s', instance._meta.verbose_name, instance.pk, self.request.user.username)

    def perform_destroy(self, instance):
        audit_log.info('删除 %s [pk=%s] by %s', instance._meta.verbose_name, instance.pk, self.request.user.username)
        instance.delete()

    @action(methods=['post'], detail=False)
    def batch_delete(self, request):
        ids = request.data.get('ids', [])
        model = self.get_queryset().model
        model.objects.filter(id__in=ids).delete()
        audit_log.info('批量删除 %s ids=%s by %s', model._meta.verbose_name, ids, request.user.username)
        return Response({'msg': '删除成功'})