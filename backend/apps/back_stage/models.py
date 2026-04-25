from apps.common_views.models import CommonDatetime
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser, CommonDatetime):
    dd_user_id = models.CharField(verbose_name="钉钉ID", max_length=128, blank=True, null=True)
    phone_number = models.CharField(verbose_name="手机号", max_length=16, unique=True)
    avatar = models.URLField(verbose_name="头像", blank=True, null=True)
    is_default_password = models.BooleanField(verbose_name="是否默认密码", default=False)
    department = models.CharField(verbose_name="部门", max_length=128, blank=True, null=True)

    def __str__(self):
        return self.username
