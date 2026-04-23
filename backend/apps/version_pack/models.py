import os

from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from apps.common_views.models import CommonDatetime
from django.core.validators import FileExtensionValidator


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        # 如果存在同名文件，则删除它
        if self.exists(name):
            self.delete(name)
        return name


class BaseEnv(CommonDatetime):
    """
    版本环境控制表
    """
    env_name = models.CharField(verbose_name="环境名称", unique=True, max_length=128)
    apply_project = models.CharField(verbose_name="适用专项", max_length=16, default='主线版本')
    env_note = models.TextField(verbose_name="环境描述", null=True, blank=True)

    class Meta:
        abstract = True


test_result_choices = (
    ('未开始', '未开始'),
    ('测试中', '测试中'),
    ('通过', '通过'),
    ('失败', '失败'),
    ('中断', '中断'),
)


class BaseVersion(CommonDatetime):
    """
    版本控制表
    """
    version_num = models.CharField(verbose_name="版本号", max_length=128, unique=True)
    versions_type = models.JSONField(verbose_name="版本类型")
    apply_project = models.CharField(verbose_name="适用专项", max_length=16, default='主线版本')
    dev_test_result = models.TextField(verbose_name="研发提测", null=True, blank=True)
    test_result = models.CharField(verbose_name="测试结果", max_length=32, choices=test_result_choices, null=True,
                                   blank=True, default="未开始")
    test_verdict = models.TextField(verbose_name="测试总结", null=True, blank=True)

    class Meta:
        abstract = True


def per_env_path(instance, filename):
    return os.path.join('per_env', str(instance.env_name), filename)


class PerEnv(BaseEnv):
    env_file = models.FileField(verbose_name="环境文件", upload_to=per_env_path)


def per_version_path(instance, filename):
    return os.path.join('per_versions', str(instance.version_num), filename)


class PerVersion(BaseVersion):
    version_file = models.FileField(verbose_name="版本文件", upload_to=per_version_path, storage=OverwriteStorage())
    env = models.ForeignKey(PerEnv, verbose_name="适用环境", on_delete=models.SET_NULL, null=True)
    database_file = models.FileField(verbose_name="数据库文件", upload_to=per_version_path, storage=OverwriteStorage(),
                                     null=True, blank=True, validators=[FileExtensionValidator(['db'])])


# ════════════════════════════════════════════════════════════════════
# 定位模块  loc_*
# ════════════════════════════════════════════════════════════════════

def loc_env_path(instance, filename):
    return os.path.join('loc_env', str(instance.env_name), filename)


class LocEnv(BaseEnv):
    env_file = models.FileField(verbose_name="环境文件", upload_to=loc_env_path)


def loc_version_path(instance, filename):
    return os.path.join('loc_versions', str(instance.version_num), filename)


class LocVersion(BaseVersion):
    version_file = models.FileField(verbose_name="版本文件", upload_to=loc_version_path, storage=OverwriteStorage())
    env = models.ForeignKey(LocEnv, verbose_name="适用环境", on_delete=models.SET_NULL, null=True)


# ════════════════════════════════════════════════════════════════════
# 控制模块  ctl_*
# ════════════════════════════════════════════════════════════════════

def ctl_env_path(instance, filename):
    return os.path.join('ctl_env', str(instance.env_name), filename)


class CtlEnv(BaseEnv):
    env_file = models.FileField(verbose_name="环境文件", upload_to=ctl_env_path)


def ctl_version_path(instance, filename):
    return os.path.join('ctl_versions', str(instance.version_num), filename)


class CtlVersion(BaseVersion):
    version_file = models.FileField(verbose_name="版本文件", upload_to=ctl_version_path, storage=OverwriteStorage())
    env = models.ForeignKey(CtlEnv, verbose_name="适用环境", on_delete=models.SET_NULL, null=True)


# ════════════════════════════════════════════════════════════════════
# 仿真模块  sim_*
# ════════════════════════════════════════════════════════════════════

def sim_env_path(instance, filename):
    return os.path.join('sim_env', str(instance.env_name), filename)


class SimEnv(BaseEnv):
    env_file = models.FileField(verbose_name="环境文件", upload_to=sim_env_path)


def sim_version_path(instance, filename):
    return os.path.join('sim_versions', str(instance.version_num), filename)


class SimVersion(BaseVersion):
    version_file = models.FileField(verbose_name="版本文件", upload_to=sim_version_path, storage=OverwriteStorage())
    env = models.ForeignKey(SimEnv, verbose_name="适用环境", on_delete=models.SET_NULL, null=True)


# ════════════════════════════════════════════════════════════════════
# 传感器模块  sen_*
# ════════════════════════════════════════════════════════════════════

def sen_env_path(instance, filename):
    return os.path.join('sen_env', str(instance.env_name), filename)


class SenEnv(BaseEnv):
    env_file = models.FileField(verbose_name="环境文件", upload_to=sen_env_path)


def sen_version_path(instance, filename):
    return os.path.join('sen_versions', str(instance.version_num), filename)


class SenVersion(BaseVersion):
    version_file = models.FileField(verbose_name="版本文件", upload_to=sen_version_path, storage=OverwriteStorage())
    env = models.ForeignKey(SenEnv, verbose_name="适用环境", on_delete=models.SET_NULL, null=True)


# ════════════════════════════════════════════════════════════════════
# post_delete 信号：删除记录时同步清理物理文件
# 覆盖单条 delete() 和 QuerySet.filter().delete()（含 batch_delete）
# ════════════════════════════════════════════════════════════════════

def _delete_filefields(instance, field_names):
    """删除 instance 上指定 FileField 的物理文件"""
    for name in field_names:
        f = getattr(instance, name, None)
        if f:
            f.delete(save=False)


_MODEL_FILE_FIELDS = [
    (PerEnv,     ['env_file']),
    (PerVersion, ['version_file', 'database_file']),
    (LocEnv,     ['env_file']),
    (LocVersion, ['version_file']),
    (CtlEnv,     ['env_file']),
    (CtlVersion, ['version_file']),
    (SimEnv,     ['env_file']),
    (SimVersion, ['version_file']),
    (SenEnv,     ['env_file']),
    (SenVersion, ['version_file']),
]


def _make_delete_handler(field_names):
    def handler(sender, instance, **kwargs):
        _delete_filefields(instance, field_names)
    return handler


for _model, _fields in _MODEL_FILE_FIELDS:
    receiver(post_delete, sender=_model)(_make_delete_handler(_fields))
