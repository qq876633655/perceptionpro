import uuid
import os
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from apps.common_views.models import CommonDatetime

# Create your models here.

target_type_choices = (
    ("pallet", "托盘"),
    ("cage", "料笼"),
)
texture_choices = (
    ('plastic', '塑料'),
    ('metal', '金属'),
    ('wood', '木材'),
    ('mirror_hollow', '镜面空洞'),
    ('plastic_damaged', '塑料破损'),
    ('mirror', '镜面'),
)

color_choices = (
    ('white', '白色'),
    ('yellow', '黄色'),
    ('blue', '蓝色'),
    ('black', '黑色'),
    ('red', '红色'),
    ('red_brown', '红棕色'),
    ('silver', '银色'),
    ('wood_color', '原木色'),
    ('black_hollow', '黑色空洞'),
    ('silver_gray', '银灰色'),
)


class GetTestTarget(CommonDatetime):
    # 筛选签
    target_name = models.CharField(verbose_name="载具名称", max_length=255, unique=True)
    target_type = models.CharField(verbose_name="类型", max_length=64, choices=target_type_choices)

    # 卡板参数
    pallet = models.CharField(verbose_name="墩宽列表", max_length=256, default="0,0,0")
    hole = models.CharField(verbose_name="孔宽列表", max_length=256, default="0,0")
    pallet_height = models.FloatField(verbose_name='墩高', default=0)
    top_height = models.FloatField(verbose_name='面板高度', default=0)
    bottom_height = models.FloatField(verbose_name='底板高度', default=0)
    card_width_expand = models.FloatField(verbose_name='面板相对墩y方向突出量', default=0)
    card_length_expand = models.FloatField(verbose_name='面板相对墩x方向突出量', default=0)
    fork_in_bias_height = models.FloatField(verbose_name='入叉高度相对横梁高度偏移量', default=0)
    adaption_z_reserve = models.FloatField(verbose_name='roi区域上下整体偏移距离', default=0)
    card_length = models.FloatField(verbose_name='卡板长度', default=0)
    card_height = models.FloatField(verbose_name='卡板高度', default=0)

    # 必填项
    texture = models.CharField(verbose_name="模型材质", max_length=16, choices=texture_choices)
    color = models.CharField(verbose_name="模型颜色", max_length=16, choices=color_choices)
    length = models.FloatField(verbose_name='入叉面长')
    width = models.FloatField(verbose_name='入叉面宽')
    height = models.FloatField(verbose_name='入叉面高')
    t_target_in_fork_center_x = models.FloatField(verbose_name='物体坐标入叉面中心点x', default=0)
    t_target_in_fork_center_y = models.FloatField(verbose_name='物体坐标入叉面中心点y', default=0)
    t_target_in_fork_center_z = models.FloatField(verbose_name='物体坐标入叉面中心点z', default=0)

    model_name = models.CharField(verbose_name="模型名称", max_length=256)
    extern_proto_path = models.CharField(verbose_name="引用路径", max_length=256)
    node_params = models.JSONField(verbose_name='节点参数')

    def __str__(self):
        return str(self.target_name)


class AgvBody(CommonDatetime):
    agv_type = models.CharField(verbose_name="测试车型", max_length=128, unique=True)
    left_width = models.FloatField(verbose_name="左边车宽")
    right_width = models.FloatField(verbose_name="右边车宽")
    front_length = models.FloatField(verbose_name="前方车长")
    back_length = models.FloatField(verbose_name="后方车长")
    fork_length = models.FloatField(verbose_name="货叉长度")
    fork_inner_width = models.FloatField(verbose_name="货叉内宽")
    fork_width = models.FloatField(verbose_name="货叉宽度")
    fork_thickness = models.FloatField(verbose_name="货叉厚度")
    load_position_x = models.FloatField(verbose_name="原车前悬距")
    sensor_extrinsic = models.TextField(verbose_name='传感器外参')
    agv_node = models.TextField(verbose_name='车体节点')

    def __str__(self):
        return str(self.agv_type)


def get_test_common_parameter_path(instance, filename):
    return os.path.join('sim_res_bak/common_parameter', str(instance.uid), filename)


class GetTestCommonParameter(CommonDatetime):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    common_parameter_name = models.CharField(verbose_name="通参名称", max_length=255, unique=True)
    sim_test_version = models.CharField(verbose_name="资产版本", max_length=255)
    sim_test_vehicle = models.CharField(verbose_name="测试车型", max_length=255)
    common_parameter_file = models.FileField(verbose_name="通用参数", upload_to=get_test_common_parameter_path,
                                             max_length=255)
    parameter_desc = models.TextField(verbose_name="通参描述", null=True, blank=True)

    def __str__(self):
        return str(self.common_parameter_name)


@receiver(pre_save, sender=GetTestCommonParameter)
def _get_test_common_param_pre_save(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = GetTestCommonParameter.objects.get(pk=instance.pk)
    except GetTestCommonParameter.DoesNotExist:
        return
    if old.common_parameter_file and old.common_parameter_file.name != instance.common_parameter_file.name:
        old.common_parameter_file.delete(save=False)


@receiver(post_delete, sender=GetTestCommonParameter)
def _get_test_common_param_post_delete(sender, instance, **kwargs):
    if instance.common_parameter_file:
        instance.common_parameter_file.delete(save=False)
