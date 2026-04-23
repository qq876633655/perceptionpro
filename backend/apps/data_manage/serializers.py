from rest_framework import serializers
from apps.data_manage.models import SimProjectProperty, SimCommonProperty


class SimProjectPropertySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='')

    class Meta:
        model = SimProjectProperty
        fields = '__all__'


class SimCommonPropertySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='')

    class Meta:
        model = SimCommonProperty
        fields = '__all__'
