import uuid

from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from apps.common_views.models import CommonDatetime
from django.core.validators import FileExtensionValidator


class BaseEnv(CommonDatetime):
    """
    版本环境控制表
    """
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
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
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    version_num = models.CharField(verbose_name="版本号", max_length=128, unique=True)
    versions_type = models.JSONField(verbose_name="版本类型")
    apply_project = models.CharField(verbose_name="适用专项", max_length=16, default='主线版本')
    dev_test_result = models.TextField(verbose_name="研发提测", null=True, blank=True)
    # 新建时不提供下面两个字段
    test_result = models.CharField(verbose_name="测试结果", max_length=32, choices=test_result_choices, null=True,
                                   blank=True, default="未开始")
    test_verdict = models.TextField(verbose_name="测试总结", null=True, blank=True)

    class Meta:
        abstract = True


# ════════════════════════════════════════════════════════════════════
# 感知模块  per_*
# ════════════════════════════════════════════════════════════════════

def per_env_path(instance, filename):
    return f'version_pack/per_env/{instance.uid}/{filename}'

class PerEnv(BaseEnv):
    env_file = models.FileField(verbose_name="环境文件", upload_to=per_env_path, max_length=512)


def per_version_path(instance, filename):
    return f'version_pack/per_ver/{instance.uid}/{filename}'

class PerVersion(BaseVersion):
    version_file = models.FileField(verbose_name="版本文件", upload_to=per_version_path, max_length=512)
    env = models.ForeignKey(PerEnv, verbose_name="适用环境", on_delete=models.SET_NULL, null=True)
    database_file = models.FileField(verbose_name="数据库文件", upload_to=per_version_path,
                                     null=True, blank=True, max_length=512, validators=[FileExtensionValidator(['db'])])


# ════════════════════════════════════════════════════════════════════
# 定位模块  loc_*
# ════════════════════════════════════════════════════════════════════

def loc_env_path(instance, filename):
    return f'version_pack/loc_env/{instance.uid}/{filename}'

class LocEnv(BaseEnv):
    env_file = models.FileField(verbose_name="环境文件", upload_to=loc_env_path, max_length=512)


def loc_version_path(instance, filename):
    return f'version_pack/loc_ver/{instance.uid}/{filename}'

class LocVersion(BaseVersion):
    version_file = models.FileField(verbose_name="版本文件", upload_to=loc_version_path, max_length=512)
    env = models.ForeignKey(LocEnv, verbose_name="适用环境", on_delete=models.SET_NULL, null=True)


# ════════════════════════════════════════════════════════════════════
# 控制模块  ctl_*
# ════════════════════════════════════════════════════════════════════

def ctl_env_path(instance, filename):
    return f'version_pack/ctl_env/{instance.uid}/{filename}'

class CtlEnv(BaseEnv):
    env_file = models.FileField(verbose_name="环境文件", upload_to=ctl_env_path, max_length=512)


def ctl_version_path(instance, filename):
    return f'version_pack/ctl_ver/{instance.uid}/{filename}'

class CtlVersion(BaseVersion):
    version_file = models.FileField(verbose_name="版本文件", upload_to=ctl_version_path, max_length=512)
    env = models.ForeignKey(CtlEnv, verbose_name="适用环境", on_delete=models.SET_NULL, null=True)


# ════════════════════════════════════════════════════════════════════
# 仿真模块  sim_*
# ════════════════════════════════════════════════════════════════════

def sim_env_path(instance, filename):
    return f'version_pack/sim_env/{instance.uid}/{filename}'

class SimEnv(BaseEnv):
    env_file = models.FileField(verbose_name="环境文件", upload_to=sim_env_path, max_length=512)


def sim_version_path(instance, filename):
    return f'version_pack/sim_ver/{instance.uid}/{filename}'

class SimVersion(BaseVersion):
    version_file = models.FileField(verbose_name="版本文件", upload_to=sim_version_path, max_length=512)
    env = models.ForeignKey(SimEnv, verbose_name="适用环境", on_delete=models.SET_NULL, null=True)


# ════════════════════════════════════════════════════════════════════
# 传感器模块  sen_*
# ════════════════════════════════════════════════════════════════════

def sen_env_path(instance, filename):
    return f'version_pack/sen_env/{instance.uid}/{filename}'

class SenEnv(BaseEnv):
    env_file = models.FileField(verbose_name="环境文件", upload_to=sen_env_path, max_length=512)


def sen_version_path(instance, filename):
    return f'version_pack/sen_ver/{instance.uid}/{filename}'

class SenVersion(BaseVersion):
    version_file = models.FileField(verbose_name="版本文件", upload_to=sen_version_path, max_length=512)
    env = models.ForeignKey(SenEnv, verbose_name="适用环境", on_delete=models.SET_NULL, null=True)


# ════════════════════════════════════════════════════════════════════
# 自动化模块  at_*
# ════════════════════════════════════════════════════════════════════

def at_env_path(instance, filename):
    return f'version_pack/at_env/{instance.uid}/{filename}'

class AtEnv(BaseEnv):
    env_file = models.FileField(verbose_name="环境文件", upload_to=at_env_path, max_length=512)


def at_version_path(instance, filename):
    return f'version_pack/at_ver/{instance.uid}/{filename}'

class AtVersion(BaseVersion):
    version_file = models.FileField(verbose_name="版本文件", upload_to=at_version_path, max_length=512)
    env = models.ForeignKey(AtEnv, verbose_name="适用环境", on_delete=models.SET_NULL, null=True)


# ════════════════════════════════════════════════════════════════════
# 文件信号：pre_save 更新时删旧文件，post_delete 删记录时删文件
# ════════════════════════════════════════════════════════════════════

# 模型 → FileField 名称列表
_FILE_SIGNAL_REGISTRY = [
    (PerEnv, ['env_file']),
    (PerVersion, ['version_file', 'database_file']),
    (LocEnv, ['env_file']),
    (LocVersion, ['version_file']),
    (CtlEnv, ['env_file']),
    (CtlVersion, ['version_file']),
    (SimEnv, ['env_file']),
    (SimVersion, ['version_file']),
    (SenEnv, ['env_file']),
    (SenVersion, ['version_file']),
    (AtEnv, ['env_file']),
    (AtVersion, ['version_file']),
]


def _make_pre_save_handler(model_cls, field_names):
    def handler(sender, instance, **kwargs):
        if not instance.pk:
            return
        try:
            old = model_cls.objects.get(pk=instance.pk)
        except model_cls.DoesNotExist:
            return
        for name in field_names:
            old_f = getattr(old, name, None)
            new_f = getattr(instance, name, None)
            old_name = old_f.name if old_f else None
            new_name = new_f.name if new_f else None
            if old_name and old_name != new_name:
                old_f.delete(save=False)

    return handler


def _make_post_delete_handler(field_names):
    def handler(sender, instance, **kwargs):
        for name in field_names:
            f = getattr(instance, name, None)
            if f:
                f.delete(save=False)

    return handler


for _model, _fields in _FILE_SIGNAL_REGISTRY:
    receiver(pre_save, sender=_model)(_make_pre_save_handler(_model, _fields))
    receiver(post_delete, sender=_model)(_make_post_delete_handler(_fields))
