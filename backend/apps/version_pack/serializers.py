import re

from rest_framework import serializers

from apps.version_pack.models import PerEnv, PerVersion, LocEnv, LocVersion, CtlEnv, CtlVersion, SimEnv, SimVersion, SenEnv, SenVersion

VERSION_NUM_RE = re.compile(r'^[a-zA-Z0-9._\-]+$')


def _version_num_validator(value):
    if not VERSION_NUM_RE.match(value):
        raise serializers.ValidationError(
            "版本号仅支持字母、数字、点(.)、横线(-)、下划线(_)，不能包含中文或特殊字符"
        )
    return value


# ════════════════════════════════════════════════════════════════════
# Per（感知）
# ════════════════════════════════════════════════════════════════════

class PerEnvSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='')

    class Meta:
        model = PerEnv
        fields = '__all__'


class PerVersionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerVersion
        exclude = ('test_result', 'test_verdict')

    def validate_version_num(self, value):
        return _version_num_validator(value)


class PerVersionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerVersion
        fields = '__all__'

    def validate(self, attrs):
        if 'version_num' in self.initial_data:
            raise serializers.ValidationError({"version_num": "版本号不允许修改"})
        if 'version_file' in self.initial_data:
            raise serializers.ValidationError({"version_file": "版本文件不允许修改"})
        return super().validate(attrs)


class PerVersionListSerializer(serializers.ModelSerializer):
    env_name = serializers.CharField(source='env.env_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='')

    class Meta:
        model = PerVersion
        fields = '__all__'


# ════════════════════════════════════════════════════════════════════
# 通用 Env / Version Serializer 工厂（loc / ctl / sim / sen 复用）
# ════════════════════════════════════════════════════════════════════

def make_env_serializer(model_cls):
    class _EnvSerializer(serializers.ModelSerializer):
        created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='')
        class Meta:
            model = model_cls
            fields = '__all__'
    _EnvSerializer.__name__ = f'{model_cls.__name__}Serializer'
    return _EnvSerializer


def make_version_create_serializer(model_cls):
    class _CreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = model_cls
            exclude = ('test_result', 'test_verdict')
        def validate_version_num(self, value):
            return _version_num_validator(value)
    _CreateSerializer.__name__ = f'{model_cls.__name__}CreateSerializer'
    return _CreateSerializer


def make_version_update_serializer(model_cls):
    class _UpdateSerializer(serializers.ModelSerializer):
        class Meta:
            model = model_cls
            fields = '__all__'
        def validate(self, attrs):
            if 'version_num' in self.initial_data:
                raise serializers.ValidationError({"version_num": "版本号不允许修改"})
            if 'version_file' in self.initial_data:
                raise serializers.ValidationError({"version_file": "版本文件不允许修改"})
            return super().validate(attrs)
    _UpdateSerializer.__name__ = f'{model_cls.__name__}UpdateSerializer'
    return _UpdateSerializer


def make_version_list_serializer(model_cls, env_model_cls):
    class _ListSerializer(serializers.ModelSerializer):
        env_name = serializers.CharField(source='env.env_name', read_only=True)
        created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='')
        class Meta:
            model = model_cls
            fields = '__all__'
    _ListSerializer.__name__ = f'{model_cls.__name__}ListSerializer'
    return _ListSerializer


# ── Loc（定位）──────────────────────────────────────────────────────
LocEnvSerializer          = make_env_serializer(LocEnv)
LocVersionCreateSerializer = make_version_create_serializer(LocVersion)
LocVersionUpdateSerializer = make_version_update_serializer(LocVersion)
LocVersionListSerializer   = make_version_list_serializer(LocVersion, LocEnv)

# ── Ctl（控制）──────────────────────────────────────────────────────
CtlEnvSerializer          = make_env_serializer(CtlEnv)
CtlVersionCreateSerializer = make_version_create_serializer(CtlVersion)
CtlVersionUpdateSerializer = make_version_update_serializer(CtlVersion)
CtlVersionListSerializer   = make_version_list_serializer(CtlVersion, CtlEnv)

# ── Sim（仿真）──────────────────────────────────────────────────────
SimEnvSerializer          = make_env_serializer(SimEnv)
SimVersionCreateSerializer = make_version_create_serializer(SimVersion)
SimVersionUpdateSerializer = make_version_update_serializer(SimVersion)
SimVersionListSerializer   = make_version_list_serializer(SimVersion, SimEnv)

# ── Sen（传感器）────────────────────────────────────────────────────
SenEnvSerializer          = make_env_serializer(SenEnv)
SenVersionCreateSerializer = make_version_create_serializer(SenVersion)
SenVersionUpdateSerializer = make_version_update_serializer(SenVersion)
SenVersionListSerializer   = make_version_list_serializer(SenVersion, SenEnv)
