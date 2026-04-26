import io
import os
import shutil
import zipfile

from django.conf import settings
from django.db import transaction
from django.http import StreamingHttpResponse
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from apps.back_stage.permissions import HasModelPermission
from apps.common_views.views import BaseModelViewSet
from apps.sim_test_agv.models import (
    CaseMap, CaseProperty,
    SchemeCommonParameter, CaseTemplate, AgvTestTask,
)
from apps.sim_test_agv.serializers import (
    CaseMapSerializer,
    CasePropertySerializer, SchemeCommonParameterSerializer,
    CaseTemplateSerializer, AgvTestTaskCreateSerializer, AgvTestTaskListSerializer,
)
from apps.sim_test_agv.filters import (
    CaseMapFilter, CasePropertyFilter,
    SchemeCommonParameterFilter, CaseTemplateFilter, AgvTestTaskFilter,
)
from apps.sim_test_agv import tasks as agv_tasks

User = get_user_model()

_PERMS = [IsAuthenticated, HasModelPermission]
_FILTER_BACKENDS = [DjangoFilterBackend, SearchFilter, OrderingFilter]

_FOLDER_FIELDS = {'lastagvpose_path', 'mapping_ecal_path', 'extend_mapping_ecal_path', 'ply_path'}


# ── CaseMap ──────────────────────────────────────────────────────────

class CaseMapViewSet(BaseModelViewSet):
    queryset = CaseMap.objects.all().order_by('-create_time')
    serializer_class = CaseMapSerializer
    permission_classes = _PERMS
    filter_backends = _FILTER_BACKENDS
    filterset_class = CaseMapFilter
    search_fields = ['district_name']
    ordering_fields = ['create_time']

    @action(methods=['get'], detail=False)
    def creators(self, request):
        ids = CaseMap.objects.exclude(created_by=None).values_list('created_by', flat=True).distinct()
        return Response(list(User.objects.filter(id__in=ids).values('id', 'username')))


# ── CaseProperty ─────────────────────────────────────────────────────

class CasePropertyViewSet(BaseModelViewSet):
    queryset = CaseProperty.objects.all().order_by('-create_time')
    serializer_class = CasePropertySerializer
    permission_classes = _PERMS
    filter_backends = _FILTER_BACKENDS
    filterset_class = CasePropertyFilter
    search_fields = ['sim_scheme_name', 'sim_test_version', 'sim_test_vehicle']
    ordering_fields = ['create_time']

    @action(methods=['post'], detail=False, url_path='batch_copy')
    def batch_copy(self, request):
        ids = request.data.get('ids', [])
        new_version = (request.data.get('sim_test_version') or '').strip()

        if not ids:
            return Response({'detail': '请选择要复制的记录'}, status=400)
        if not new_version:
            return Response({'detail': '资产版本不能为空'}, status=400)

        # 6.1 校验所有 id 存在
        records = list(CaseProperty.objects.filter(id__in=ids))
        if len(records) != len(set(ids)):
            return Response({'detail': '部分记录不存在，请刷新后重试'}, status=400)

        # 6.2 检查唯一性冲突
        conflicts = []
        for rec in records:
            if CaseProperty.objects.filter(
                sim_test_version=new_version,
                sim_test_vehicle=rec.sim_test_vehicle,
                sim_scheme_name=rec.sim_scheme_name,
            ).exists():
                conflicts.append(f'{rec.sim_test_vehicle} / {rec.sim_scheme_name}')
        if conflicts:
            return Response(
                {'detail': '以下车型+方案在目标版本下已存在：' + '；'.join(conflicts)},
                status=400,
            )

        # ── 辅助函数 ──────────────────────────────────────────────
        def _remap(path, old_ver):
            """替换路径 sim_res_bak/{old_ver}/... 中的版本段"""
            if not path:
                return path
            parts = path.replace('\\', '/').split('/')
            if len(parts) >= 2 and parts[1] == old_ver:
                parts[1] = new_version
            return '/'.join(parts)

        copied_abs = []  # 已创建的物理路径，失败时用于回滚

        def _copy_file(old_rel, new_rel):
            if not old_rel or not new_rel:
                return
            src = os.path.join(settings.MEDIA_ROOT, old_rel)
            dst = os.path.join(settings.MEDIA_ROOT, new_rel)
            if os.path.isfile(src):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                copied_abs.append(dst)

        def _copy_folder(old_rel, new_rel):
            if not old_rel or not new_rel:
                return
            src = os.path.join(settings.MEDIA_ROOT, old_rel)
            dst = os.path.join(settings.MEDIA_ROOT, new_rel)
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                copied_abs.append(dst)

        def _rollback_files():
            for p in copied_abs:
                try:
                    if os.path.isfile(p):
                        os.remove(p)
                    elif os.path.isdir(p):
                        shutil.rmtree(p, ignore_errors=True)
                except Exception:
                    pass

        # ── 6.3 复制 ──────────────────────────────────────────────
        _CHAR_FOLDER_FIELDS = (
            'lastagvpose_path', 'mapping_ecal_path',
            'extend_mapping_ecal_path', 'ply_path',
        )

        new_instances = []
        try:
            for rec in records:
                old_ver = rec.sim_test_version

                new_backup = _remap(rec.backup_file.name if rec.backup_file else '', old_ver)
                new_wbt = _remap(rec.wbt_file.name if rec.wbt_file else '', old_ver)
                _copy_file(rec.backup_file.name if rec.backup_file else None, new_backup)
                _copy_file(rec.wbt_file.name if rec.wbt_file else None, new_wbt)

                new_char_paths = {}
                for field in _CHAR_FOLDER_FIELDS:
                    old_path = getattr(rec, field, '') or ''
                    new_path = _remap(old_path, old_ver) if old_path else None
                    if new_path:
                        _copy_folder(old_path, new_path)
                    new_char_paths[field] = new_path

                new_instances.append(CaseProperty(
                    sim_test_version=new_version,
                    sim_test_vehicle=rec.sim_test_vehicle,
                    sim_scheme_name=rec.sim_scheme_name,
                    test_module=rec.test_module,
                    backup_file=new_backup,
                    wbt_file=new_wbt,
                    map=rec.map,
                    property_status=rec.property_status,
                    created_by=request.user,
                    **new_char_paths,
                ))
        except Exception as e:
            _rollback_files()
            return Response({'detail': f'文件复制失败：{str(e)}'}, status=500)

        try:
            with transaction.atomic():
                for inst in new_instances:
                    inst.save()
        except Exception as e:
            _rollback_files()
            return Response({'detail': f'数据保存失败：{str(e)}'}, status=500)

        return Response({'msg': f'复制成功，共复制 {len(new_instances)} 条记录'})

    @action(methods=['get'], detail=False)
    def creators(self, request):
        ids = CaseProperty.objects.exclude(created_by=None).values_list('created_by', flat=True).distinct()
        return Response(list(User.objects.filter(id__in=ids).values('id', 'username')))

    @action(methods=['get'], detail=False, url_path='sim_test_versions')
    def sim_test_versions(self, request):
        """返回 CaseProperty.sim_test_version 去重列表，供 AgvTestTask 新建时下拉选择"""
        values = (CaseProperty.objects
                  .values_list('sim_test_version', flat=True)
                  .distinct()
                  .order_by('sim_test_version'))
        return Response(list(values))

    @action(methods=['get'], detail=False, url_path='choices')
    def choices(self, request):
        """返回各字段当前已有的去重值，供前端下拉/datalist"""
        def distinct_values(field):
            return list(
                CaseProperty.objects.exclude(**{field: ''})
                .values_list(field, flat=True).distinct().order_by(field)
            )
        return Response({
            'sim_test_version': distinct_values('sim_test_version'),
            'sim_test_vehicle': distinct_values('sim_test_vehicle'),
            'sim_scheme_name': distinct_values('sim_scheme_name'),
            'test_module': distinct_values('test_module'),
        })

    @action(methods=['post'], detail=True, url_path='upload_folder_field')
    def upload_folder_field(self, request, pk=None):
        """
        上传文件夹到指定路径字段。
        body: field_name, files[], paths[] (webkitRelativePath)
        files 会保存到 sim_res_bak/{ver}/{vehicle}/{scheme}/{field_name}/ 下，保留目录结构。
        """
        field_name = request.data.get('field_name', '')
        if field_name not in _FOLDER_FIELDS:
            return Response({'detail': f'field_name 须为 {_FOLDER_FIELDS} 之一'}, status=400)

        instance = self.get_object()
        files = request.FILES.getlist('files')
        paths = request.POST.getlist('paths')

        if not files:
            return Response({'detail': '未收到文件'}, status=400)
        if len(files) != len(paths):
            return Response({'detail': 'files 与 paths 数量不匹配'}, status=400)

        # 目标基础目录：sim_res_bak/{ver}/{vehicle}/{scheme}/
        base_dir = os.path.join(
            'sim_res_bak',
            str(instance.sim_test_version),
            str(instance.sim_test_vehicle),
            str(instance.sim_scheme_name),
        )

        # 删除旧文件夹
        old_path = getattr(instance, field_name, '') or ''
        if old_path:
            abs_old = os.path.join(settings.MEDIA_ROOT, old_path)
            if os.path.exists(abs_old):
                shutil.rmtree(abs_old)

        # 写入所有文件，保留相对目录结构
        for file, rel_path in zip(files, paths):
            abs_path = os.path.join(settings.MEDIA_ROOT, base_dir, rel_path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)

        folder_root = paths[0].split('/')[0]
        folder_path = os.path.join(base_dir, folder_root)
        setattr(instance, field_name, folder_path)
        instance.save(update_fields=[field_name])
        return Response({'msg': '上传成功', 'path': folder_path})

    @action(methods=['get'], detail=True, url_path='download_folder_field')
    def download_folder_field(self, request, pk=None):
        """打包指定路径字段的文件夹为 zip 下载"""
        field_name = request.query_params.get('field_name', '')
        if field_name not in _FOLDER_FIELDS:
            return Response({'detail': '无效的 field_name'}, status=400)

        instance = self.get_object()
        folder_path = getattr(instance, field_name, '') or ''
        if not folder_path:
            return Response({'detail': '该字段暂无文件夹'}, status=404)

        abs_folder = os.path.join(settings.MEDIA_ROOT, folder_path)
        if not os.path.exists(abs_folder):
            return Response({'detail': '服务器文件夹不存在'}, status=404)

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for dirpath, _, filenames in os.walk(abs_folder):
                for fname in filenames:
                    abs_file = os.path.join(dirpath, fname)
                    arcname = os.path.relpath(abs_file, os.path.dirname(abs_folder))
                    zf.write(abs_file, arcname)
        buf.seek(0)

        folder_name = os.path.basename(abs_folder)
        response = StreamingHttpResponse(buf, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{folder_name}.zip"'
        return response


# ── SchemeCommonParameter ────────────────────────────────────────────

class SchemeCommonParameterViewSet(BaseModelViewSet):
    queryset = SchemeCommonParameter.objects.all().order_by('-create_time')
    serializer_class = SchemeCommonParameterSerializer
    permission_classes = _PERMS
    filter_backends = _FILTER_BACKENDS
    filterset_class = SchemeCommonParameterFilter
    search_fields = ['common_parameter_name']
    ordering_fields = ['create_time']

    @action(methods=['post'], detail=False, url_path='batch_copy')
    def batch_copy(self, request):
        items = request.data.get('items', [])
        if not items:
            return Response({'detail': '请选择要复制的记录'}, status=400)

        ids = [item.get('id') for item in items]
        new_names = [str(item.get('common_parameter_name') or '').strip() for item in items]

        # 6.1 校验所有 id 存在
        records_map = {r.id: r for r in SchemeCommonParameter.objects.filter(id__in=ids)}
        missing = [str(i) for i in ids if i not in records_map]
        if missing:
            return Response({'detail': f'以下记录不存在，请刷新后重试：{", ".join(missing)}'}, status=400)

        # 6.2 校验新通参名称不为空
        empty_idx = [str(i + 1) for i, n in enumerate(new_names) if not n]
        if empty_idx:
            return Response({'detail': f'第 {", ".join(empty_idx)} 行通参名称不能为空'}, status=400)

        # 6.2 校验新通参名称不重复（输入间互相 + 数据库已有）
        if len(set(new_names)) != len(new_names):
            return Response({'detail': '输入的通参名称中存在重复'}, status=400)
        existing = set(
            SchemeCommonParameter.objects
            .filter(common_parameter_name__in=new_names)
            .values_list('common_parameter_name', flat=True)
        )
        if existing:
            return Response({'detail': f'以下通参名称已存在：{", ".join(existing)}'}, status=400)

        # ── 辅助：拷贝文件 ──────────────────────────────────────
        import uuid as _uuid
        copied_abs = []

        def _copy_common_file(old_rel, new_uid):
            """把旧文件拷到 sim_res_bak/common_parameter/{new_uid}/{filename}，返回新相对路径"""
            if not old_rel:
                return ''
            filename = os.path.basename(old_rel)
            new_rel = os.path.join('sim_res_bak', 'common_parameter', str(new_uid), filename)
            src = os.path.join(settings.MEDIA_ROOT, old_rel)
            dst = os.path.join(settings.MEDIA_ROOT, new_rel)
            if os.path.isfile(src):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                copied_abs.append(dst)
            return new_rel

        def _rollback():
            for p in copied_abs:
                try:
                    if os.path.isfile(p):
                        os.remove(p)
                except Exception:
                    pass

        # ── 6.3 复制 ───────────────────────────────────────────
        new_instances = []
        try:
            for item, new_name in zip(items, new_names):
                rec = records_map[item['id']]
                new_uid = _uuid.uuid4()
                old_file = rec.common_parameter_file.name if rec.common_parameter_file else ''
                new_file = _copy_common_file(old_file, new_uid)
                new_instances.append(SchemeCommonParameter(
                    uid=new_uid,
                    common_parameter_name=new_name,
                    sim_test_version=rec.sim_test_version,
                    sim_test_vehicle=rec.sim_test_vehicle,
                    test_module=rec.test_module,
                    common_parameter_status=rec.common_parameter_status,
                    parameter_desc=rec.parameter_desc,
                    common_parameter_file=new_file,
                    created_by=request.user,
                ))
        except Exception as e:
            _rollback()
            return Response({'detail': f'文件复制失败：{str(e)}'}, status=500)

        try:
            with transaction.atomic():
                for inst in new_instances:
                    inst.save()
        except Exception as e:
            _rollback()
            return Response({'detail': f'数据保存失败：{str(e)}'}, status=500)

        return Response({'msg': f'复制成功，共复制 {len(new_instances)} 条记录'})

    @action(methods=['get'], detail=False)
    def creators(self, request):
        ids = SchemeCommonParameter.objects.exclude(created_by=None).values_list('created_by', flat=True).distinct()
        return Response(list(User.objects.filter(id__in=ids).values('id', 'username')))

    @action(methods=['get'], detail=False, url_path='choices')
    def choices(self, request):
        def distinct_values(field):
            return list(
                SchemeCommonParameter.objects.exclude(**{field: ''})
                .values_list(field, flat=True).distinct().order_by(field)
            )
        return Response({
            'sim_test_version': distinct_values('sim_test_version'),
            'sim_test_vehicle': distinct_values('sim_test_vehicle'),
            'test_module': distinct_values('test_module'),
            'common_parameter_name': distinct_values('common_parameter_name'),
        })


# ── CaseTemplate ─────────────────────────────────────────────────────

class CaseTemplateViewSet(BaseModelViewSet):
    queryset = CaseTemplate.objects.all().order_by('-create_time')
    serializer_class = CaseTemplateSerializer
    permission_classes = _PERMS
    filter_backends = _FILTER_BACKENDS
    filterset_class = CaseTemplateFilter
    search_fields = ['sim_test_version', 'test_module']
    ordering_fields = ['create_time']

    @action(methods=['get'], detail=False)
    def creators(self, request):
        ids = CaseTemplate.objects.exclude(created_by=None).values_list('created_by', flat=True).distinct()
        return Response(list(User.objects.filter(id__in=ids).values('id', 'username')))

    @action(methods=['get'], detail=False, url_path='choices')
    def choices(self, request):
        def distinct_values(field):
            return list(
                CaseTemplate.objects.exclude(**{field: ''})
                .values_list(field, flat=True).distinct().order_by(field)
            )
        return Response({
            'sim_test_version': distinct_values('sim_test_version'),
            'test_module': distinct_values('test_module'),
        })


# ── AgvTestTask ──────────────────────────────────────────────────────

class AgvTestTaskViewSet(BaseModelViewSet):
    queryset = AgvTestTask.objects.all().order_by('-create_time')
    permission_classes = _PERMS
    filter_backends = _FILTER_BACKENDS
    filterset_class = AgvTestTaskFilter
    search_fields = ['sim_test_version', 'queue_name']
    ordering_fields = ['create_time']

    def get_serializer_class(self):
        if self.action == 'create':
            return AgvTestTaskCreateSerializer
        return AgvTestTaskListSerializer

    def perform_create(self, serializer):
        """保存后立即派发 Celery 任务，并回写 celery_id"""
        instance = serializer.save(
            created_by=self.request.user,
            task_status='DISPATCHED',
        )
        queue_name = instance.queue_name
        celery_task = agv_tasks.agv_sim_test_task.apply_async(
            args=[instance.id],
            queue=queue_name,
        )
        instance.celery_id = celery_task.id
        instance.save(update_fields=['celery_id'])

    @action(methods=['post'], detail=True)
    def cancel(self, request, pk=None):
        """取消任务：DISPATCHED 直接撤销；RUNNING 设标志位由 task 轮询处理"""
        instance = self.get_object()
        task_status = instance.task_status

        if task_status not in ('RUNNING', 'DISPATCHED'):
            return Response({'detail': '当前任务状态不可取消'}, status=400)

        if task_status == 'DISPATCHED':
            # 任务还在队列中，直接撤销，不需要杀进程
            if instance.celery_id:
                from dev_perceptionpro.celery import per_celery
                per_celery.control.revoke(instance.celery_id, terminate=False)
            instance.cancel_requested = True
            instance.task_status = 'CANCELED'
            instance.save(update_fields=['task_status', 'cancel_requested'])

        elif task_status == 'RUNNING':
            # 任务已在运行，先设标志位让 task 轮询到后自行终止
            instance.cancel_requested = True
            instance.save(update_fields=['cancel_requested'])
            if instance.celery_id:
                from dev_perceptionpro.celery import per_celery
                per_celery.control.revoke(instance.celery_id, terminate=False)

        return Response({'msg': '取消请求已发送'})

    @action(methods=['get'], detail=False)
    def creators(self, request):
        ids = AgvTestTask.objects.exclude(created_by=None).values_list('created_by', flat=True).distinct()
        return Response(list(User.objects.filter(id__in=ids).values('id', 'username')))
