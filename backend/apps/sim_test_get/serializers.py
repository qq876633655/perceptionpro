from rest_framework import serializers
from apps.sim_test_get.models import GetTestTarget, AgvBody, GetTestCommonParameter


class GetTestTargetSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='')
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True, default='')

    class Meta:
        model = GetTestTarget
        fields = '__all__'


class AgvBodySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='')
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True, default='')

    class Meta:
        model = AgvBody
        fields = '__all__'


class GetTestCommonParameterSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='')
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True, default='')

    class Meta:
        model = GetTestCommonParameter
        fields = '__all__'
