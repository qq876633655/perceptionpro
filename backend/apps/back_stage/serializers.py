from rest_framework import serializers
from apps.back_stage.models import User
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'phone_number',
            'avatar',
            'dd_user_id',
            'password',
            'is_staff',
            'is_superuser',
            'create_time',
            'update_time',
            'created_by',
            'updated_by',
        ]

    def create(self, validated_data):
        password = validated_data.get('password')

        if not password:
            password = 'Test123456'

        validated_data['password'] = make_password(password)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.get('password', None)

        if password:
            validated_data['password'] = make_password(password)

        return super().update(instance, validated_data)


class UserMeSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = ['password']

    def get_roles(self, obj):
        return list(obj.groups.values_list('name', flat=True))

    def get_permissions(self, obj):
        # Django权限系统自带
        return list(obj.get_all_permissions())