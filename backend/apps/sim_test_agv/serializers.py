from rest_framework import serializers
from apps.sim_test_agv.models import (
    CaseMap, CaseProperty,
    SchemeCommonParameter, CaseTemplate, AgvTestTask, WorkerNode,
)


class CaseMapSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='')
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True, default='')

    class Meta:
        model = CaseMap
        fields = '__all__'


class CasePropertySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='')
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True, default='')
    map_district_name = serializers.CharField(source='map.district_name', read_only=True, default='')
    # 4 个文件夹路径字段允许为空（上传后回填）
    lastagvpose_path = serializers.CharField(allow_blank=True, required=False, default='')
    mapping_ecal_path = serializers.CharField(allow_blank=True, required=False, default='')
    extend_mapping_ecal_path = serializers.CharField(allow_blank=True, required=False, default='')
    ply_path = serializers.CharField(allow_blank=True, required=False, default='')

    def update(self, instance, validated_data):
        # 修改时禁止变更路径三元组
        for field in ('sim_test_version', 'sim_test_vehicle', 'sim_scheme_name'):
            validated_data.pop(field, None)
        return super().update(instance, validated_data)

    class Meta:
        model = CaseProperty
        fields = '__all__'


class SchemeCommonParameterSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='')
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True, default='')

    class Meta:
        model = SchemeCommonParameter
        fields = '__all__'


class CaseTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='')
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True, default='')

    class Meta:
        model = CaseTemplate
        fields = '__all__'


class AgvTestTaskCreateSerializer(serializers.ModelSerializer):
    """新建时仅接收允许的字段"""
    class Meta:
        model = AgvTestTask
        fields = [
            'per_version', 'loc_version', 'ctl_version', 'agv_version',
            'agv_case_file', 'sim_test_version', 'queue_name',
            'recovery_default_version', 'base_version', 'target_worker',
        ]


class AgvTestTaskListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='')

    class Meta:
        model = AgvTestTask
        fields = '__all__'


class WorkerNodeSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='')
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True, default='')

    class Meta:
        model = WorkerNode
        fields = '__all__'
