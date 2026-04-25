import uuid
import os
import shutil

from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from apps.common_views.models import CommonDatetime


def versions_file_path(instance, filename):
    return os.path.join('at_versions', str(instance.uid), filename)


class AutoTestVersions(CommonDatetime):
    """
    版本控制表
    """
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    versions = models.CharField(verbose_name="版本号", max_length=128, unique=True)
    versions_file = models.FileField(verbose_name="版本文件", upload_to=versions_file_path, max_length=256)
    release_note = models.TextField(verbose_name="发布说明", null=True, blank=True)

    def __str__(self):
        return self.versions


class CaseMap(CommonDatetime):
    district_name = models.CharField(verbose_name="分区名称", max_length=255, unique=True)
    map_file = models.FileField(verbose_name="地图文件", upload_to="sim_res_bak/map/", max_length=255)

    def __str__(self):
        return str(self.district_name)


def case_property_path(instance, filename):
    return os.path.join("sim_res_bak", str(instance.sim_test_version), str(instance.sim_test_vehicle),
                        str(instance.sim_scheme_name), filename)


property_status_choices = (
    ('正常', '正常'),
    ('维护', '维护'),
)


class CaseProperty(CommonDatetime):
    sim_test_version = models.CharField(verbose_name="资产版本", max_length=255)
    sim_test_vehicle = models.CharField(verbose_name="测试车型", max_length=255)
    sim_scheme_name = models.CharField(verbose_name="测试方案", max_length=255)
    test_module = models.CharField(verbose_name="测试模块", max_length=255)
    backup_file = models.FileField(verbose_name="robotune备份", upload_to=case_property_path, max_length=255)
    lastagvpose_path = models.CharField(verbose_name="lastagvpose", max_length=128)
    wbt_file = models.FileField(verbose_name="wbt文件", upload_to=case_property_path, max_length=255)
    map = models.ForeignKey(CaseMap, verbose_name="分区名称", on_delete=models.SET_NULL, null=True)
    mapping_ecal_path = models.CharField(verbose_name="自动建图ecal", max_length=255, null=True, blank=True)
    extend_mapping_ecal_path = models.CharField(verbose_name="扩展建图ecal", max_length=255, null=True, blank=True)
    ply_path = models.CharField(verbose_name="感知模版路径", max_length=255, null=True, blank=True)
    property_status = models.CharField(verbose_name="资产状态", max_length=32, choices=property_status_choices,
                                       default="正常")

    def __str__(self):
        return str(self.sim_scheme_name + '_' + self.sim_test_vehicle + '_' + self.sim_scheme_name)

    class Meta:
        unique_together = ('sim_test_version', 'sim_test_vehicle', 'sim_scheme_name')


def common_parameter_path(instance, filename):
    return os.path.join('sim_res_bak/common_parameter', str(instance.uid), filename)


common_parameter_status_choices = (
    ('正常', '正常'),
    ('维护', '维护'),
)


class SchemeCommonParameter(CommonDatetime):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    common_parameter_name = models.CharField(verbose_name="通参名称", max_length=255, unique=True)
    sim_test_version = models.CharField(verbose_name="资产版本", max_length=255)
    sim_test_vehicle = models.CharField(verbose_name="测试车型", max_length=255)
    test_module = models.CharField(verbose_name="测试模块", max_length=255)
    common_parameter_status = models.CharField(verbose_name="通参状态", max_length=32,
                                               choices=common_parameter_status_choices, default="正常")
    parameter_desc = models.TextField(verbose_name="通参描述", null=True, blank=True)
    common_parameter_file = models.FileField(verbose_name="通用参数", upload_to=common_parameter_path, max_length=255)

    def __str__(self):
        return str(self.common_parameter_name)


def case_template_path(instance, filename):
    return os.path.join("sim_res_bak/case_template", str(instance.uid), filename)


class CaseTemplate(CommonDatetime):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sim_test_version = models.CharField(verbose_name="资产版本", max_length=255)
    test_module = models.CharField(verbose_name="测试模块", max_length=255)
    case_desc = models.TextField(verbose_name="用例说明")
    case_file = models.FileField(verbose_name="用例文件", upload_to=case_template_path, max_length=255)


def agv_test_task_path(instance, filename):
    return os.path.join("sim_res_bak/agv_test_task", str(instance.uid), filename)


manual_error_handling_choices = (
    ('True', 'True'),
    ('False', 'False'),
)

recovery_default_version_choices = (
    ('True', 'True'),
    ('False', 'False'),
)

celery_task_status_choices = (
    ('CREATED', '已创建'),
    ('DISPATCHED', '已下发'),
    ('RUNNING', '执行中'),
    ('CANCELING', '取消中'),
    ('CANCELED', '已取消'),
    ('SUCCESS', '成功'),
    ('FAILED', '失败'),
)


class AgvTestTask(CommonDatetime):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    per_version = models.FileField(verbose_name="感知测试版本", upload_to=agv_test_task_path, null=True, blank=True,
                                   max_length=255)
    loc_version = models.FileField(verbose_name="定位测试版本", upload_to=agv_test_task_path, null=True, blank=True,
                                   max_length=255)
    ctl_version = models.FileField(verbose_name="控制测试版本", upload_to=agv_test_task_path, null=True, blank=True,
                                   max_length=255)
    agv_version = models.FileField(verbose_name="整车测试版本", upload_to=agv_test_task_path, null=True, blank=True,
                                   max_length=255)
    agv_case_file = models.FileField(verbose_name="测试用例", upload_to=agv_test_task_path, max_length=255)
    sim_test_version = models.CharField(verbose_name="使用资产版本", max_length=255)
    queue_name = models.CharField(verbose_name='任务队列', max_length=255)
    recovery_default_version = models.CharField(verbose_name="是否恢复默认版本", max_length=16,
                                                choices=recovery_default_version_choices, default='False')
    base_version = models.CharField(verbose_name="待测基线版本", max_length=255, null=True, blank=True)
    manual_error_handling = models.CharField(verbose_name="是否手动处理错误", max_length=16,
                                             choices=manual_error_handling_choices, default='True')

    task_status = models.CharField(verbose_name="任务状态", max_length=16, null=True, blank=True,
                                   choices=celery_task_status_choices, default='CREATED')
    current_schedule = models.CharField(verbose_name="当前进度", max_length=32, null=True, blank=True)
    celery_id = models.CharField(verbose_name="执行中的celery_id", max_length=255, null=True, blank=True)
    process_id = models.CharField(verbose_name="执行中的task_process_id", max_length=255, null=True, blank=True)
    worker_name = models.CharField(verbose_name="执行端", max_length=128, null=True, blank=True)
    error_msg = models.TextField(verbose_name="错误信息", null=True, blank=True)
    cancel_requested = models.BooleanField(verbose_name="是否中止", default=False)

    auto_test_run_log = models.FileField(verbose_name="运行日志", upload_to=agv_test_task_path, null=True, blank=True,
                                         max_length=255)
    test_result = models.FileField(verbose_name="测试结果", upload_to=agv_test_task_path, null=True, blank=True,
                                   max_length=255)


# ════════════════════════════════════════════════════════════════════
# 文件信号
# ════════════════════════════════════════════════════════════════════

# ── AutoTestVersions ─────────────────────────────────────────────────
@receiver(pre_save, sender=AutoTestVersions)
def _at_versions_pre_save(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = AutoTestVersions.objects.get(pk=instance.pk)
    except AutoTestVersions.DoesNotExist:
        return
    if old.versions_file and old.versions_file.name != instance.versions_file.name:
        old.versions_file.delete(save=False)


@receiver(post_delete, sender=AutoTestVersions)
def _at_versions_post_delete(sender, instance, **kwargs):
    if instance.versions_file:
        instance.versions_file.delete(save=False)


# ── CaseMap ───────────────────────────────────────────────────────────
@receiver(pre_save, sender=CaseMap)
def _case_map_pre_save(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = CaseMap.objects.get(pk=instance.pk)
    except CaseMap.DoesNotExist:
        return
    if old.map_file and old.map_file.name != instance.map_file.name:
        old.map_file.delete(save=False)


@receiver(post_delete, sender=CaseMap)
def _case_map_post_delete(sender, instance, **kwargs):
    if instance.map_file:
        instance.map_file.delete(save=False)


# ── CaseProperty ──────────────────────────────────────────────────────
def _delete_folder(path):
    """删除 MEDIA_ROOT 下的文件夹（若存在）"""
    if path:
        abs_path = os.path.join(settings.MEDIA_ROOT, path)
        if os.path.exists(abs_path):
            shutil.rmtree(abs_path, ignore_errors=True)


@receiver(pre_save, sender=CaseProperty)
def _case_property_pre_save(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = CaseProperty.objects.get(pk=instance.pk)
    except CaseProperty.DoesNotExist:
        return
    # FileField：仅当文件名发生改变时才删除旧文件
    if old.backup_file and old.backup_file.name != instance.backup_file.name:
        old.backup_file.delete(save=False)
    if old.wbt_file and old.wbt_file.name != instance.wbt_file.name:
        old.wbt_file.delete(save=False)
    # CharField 路径文件夹：仅当路径发生改变时才删除旧文件夹
    for field in ('lastagvpose_path', 'mapping_ecal_path', 'extend_mapping_ecal_path', 'ply_path'):
        old_path = getattr(old, field, '') or ''
        new_path = getattr(instance, field, '') or ''
        if old_path and old_path != new_path:
            _delete_folder(old_path)


@receiver(post_delete, sender=CaseProperty)
def _case_property_post_delete(sender, instance, **kwargs):
    if instance.backup_file:
        instance.backup_file.delete(save=False)
    if instance.wbt_file:
        instance.wbt_file.delete(save=False)
    for field in ('lastagvpose_path', 'mapping_ecal_path', 'extend_mapping_ecal_path', 'ply_path'):
        _delete_folder(getattr(instance, field, ''))


# ── SchemeCommonParameter ─────────────────────────────────────────────
@receiver(pre_save, sender=SchemeCommonParameter)
def _common_param_pre_save(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = SchemeCommonParameter.objects.get(pk=instance.pk)
    except SchemeCommonParameter.DoesNotExist:
        return
    if old.common_parameter_file and old.common_parameter_file.name != instance.common_parameter_file.name:
        old.common_parameter_file.delete(save=False)


@receiver(post_delete, sender=SchemeCommonParameter)
def _common_param_post_delete(sender, instance, **kwargs):
    if instance.common_parameter_file:
        instance.common_parameter_file.delete(save=False)


# ── CaseTemplate ──────────────────────────────────────────────────────
@receiver(pre_save, sender=CaseTemplate)
def _case_template_pre_save(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = CaseTemplate.objects.get(pk=instance.pk)
    except CaseTemplate.DoesNotExist:
        return
    if old.case_file and old.case_file.name != instance.case_file.name:
        old.case_file.delete(save=False)


@receiver(post_delete, sender=CaseTemplate)
def _case_template_post_delete(sender, instance, **kwargs):
    if instance.case_file:
        instance.case_file.delete(save=False)


# ── AgvTestTask ───────────────────────────────────────────────────────
_AGV_TASK_FILE_FIELDS = (
    'per_version', 'loc_version', 'ctl_version', 'agv_version',
    'agv_case_file', 'auto_test_run_log', 'test_result',
)


@receiver(pre_save, sender=AgvTestTask)
def _agv_test_task_pre_save(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = AgvTestTask.objects.get(pk=instance.pk)
    except AgvTestTask.DoesNotExist:
        return
    for field in _AGV_TASK_FILE_FIELDS:
        old_f = getattr(old, field, None)
        new_f = getattr(instance, field, None)
        old_name = old_f.name if old_f else None
        new_name = new_f.name if new_f else None
        if old_name and old_name != new_name:
            old_f.delete(save=False)


@receiver(post_delete, sender=AgvTestTask)
def _agv_test_task_post_delete(sender, instance, **kwargs):
    for field in _AGV_TASK_FILE_FIELDS:
        f = getattr(instance, field, None)
        if f:
            f.delete(save=False)
