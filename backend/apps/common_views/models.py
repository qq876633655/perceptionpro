from django.db import models
from django.conf import settings
# Create your models here.

class CommonDatetime(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="created_%(class)s_set",
        on_delete=models.SET_NULL
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="updated_%(class)s_set",
        on_delete=models.SET_NULL
    )
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, )
    update_time = models.DateTimeField(verbose_name="更新时间", auto_now=True, )

    class Meta:
        abstract = True
