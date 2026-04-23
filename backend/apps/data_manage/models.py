import os
import uuid
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from apps.common_views.models import CommonDatetime
from apps.version_pack.models import OverwriteStorage


def project_property_path(instance, filename):
    return os.path.join('sim_project_property', str(instance.uid), filename)


class SimProjectProperty(CommonDatetime):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    apply_project = models.CharField(verbose_name="适用项目", max_length=64)
    project_property = models.FileField(verbose_name='项目资产', upload_to=project_property_path, max_length=256,
                                        storage=OverwriteStorage())
    property_desc = models.TextField(verbose_name="资产说明", null=True, blank=True)
    property_tag = models.CharField(verbose_name="标签", max_length=128, null=True, blank=True)

    def __str__(self):
        return str(self.apply_project)


@receiver(pre_save, sender=SimProjectProperty)
def _sim_project_property_delete_old_file(sender, instance, **kwargs):
    """更新时，若替换了文件，自动删除旧文件"""
    if not instance.pk:
        return
    try:
        old = SimProjectProperty.objects.get(pk=instance.pk)
    except SimProjectProperty.DoesNotExist:
        return
    if old.project_property and old.project_property != instance.project_property:
        old.project_property.delete(save=False)


@receiver(post_delete, sender=SimProjectProperty)
def _sim_project_property_delete_file(sender, instance, **kwargs):
    """删除记录时，同步删除物理文件"""
    if instance.project_property:
        instance.project_property.delete(save=False)


def common_property_path(instance, filename):
    return os.path.join('sim_common_property', str(instance.uid), filename)


class SimCommonProperty(CommonDatetime):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    versions = models.CharField(verbose_name="版本号", max_length=128, unique=True)
    common_property = models.FileField(verbose_name="通用资产", upload_to=common_property_path, max_length=256,
                                       storage=OverwriteStorage())
    property_desc = models.TextField(verbose_name="资产说明", null=True, blank=True)
    property_tag = models.CharField(verbose_name="标签", max_length=128, null=True, blank=True)

    def __str__(self):
        return str(self.versions)


@receiver(post_delete, sender=SimCommonProperty)
def _sim_common_property_delete_file(sender, instance, **kwargs):
    """删除记录时，同步删除物理文件"""
    if instance.common_property:
        instance.common_property.delete(save=False)
