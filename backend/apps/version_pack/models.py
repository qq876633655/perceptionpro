import os

from django.core.files.storage import FileSystemStorage
from django.db import models
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
    database_file = models.FileField(verbose_name="数据库文件", null=True,
                                     blank=True, validators=[FileExtensionValidator(['db'])])
    test_result = models.CharField(verbose_name="测试结果", max_length=32, choices=test_result_choices, null=True,
                                   blank=True, default="未开始")
    test_verdict = models.TextField(verbose_name="测试总结", null=True, blank=True)

    class Meta:
        abstract = True


def per_env_path(instance, filename):
    return os.path.join('per_env', str(instance.env_name), filename)


class PerEnv(BaseEnv):
    env_file = models.FileField(verbose_name="环境文件", upload_to=per_env_path)

    class Meta:
        db_table = "per_env"


def per_version_path(instance, filename):
    return os.path.join('per_versions', str(instance.version_num), filename)


class PerVersion(BaseVersion):
    version_file = models.FileField(verbose_name="版本文件", upload_to=per_version_path, storage=OverwriteStorage())
    env = models.ForeignKey(PerEnv, verbose_name="适用环境", on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "per_version"
