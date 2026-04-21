from rest_framework import serializers

from apps.version_pack.models import PerEnv, PerVersion


class PerEnvSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerEnv
        fields = '__all__'


# ✅ 创建（不包含测试字段）
class PerVersionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerVersion
        exclude = ('test_result', 'test_verdict')


# ✅ 更新（禁止改版本号 + 文件）
class PerVersionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerVersion
        fields = '__all__'

    def validate(self, attrs):
        if 'version_num' in self.initial_data:
            raise serializers.ValidationError({
                "version_num": "版本号不允许修改"
            })

        if 'version_file' in self.initial_data:
            raise serializers.ValidationError({
                "version_file": "版本文件不允许修改"
            })

        return super().validate(attrs)


# ✅ 列表展示
class PerVersionListSerializer(serializers.ModelSerializer):
    env_name = serializers.CharField(source='env.env_name', read_only=True)

    class Meta:
        model = PerVersion
        fields = '__all__'
