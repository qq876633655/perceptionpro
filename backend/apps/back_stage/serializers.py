import re

from rest_framework import serializers
from apps.back_stage.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model

PHONE_RE = re.compile(r'^1[3-9]\d{9}$')


class PermissionSerializer(serializers.ModelSerializer):
    app_label = serializers.CharField(source='content_type.app_label', read_only=True)

    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'app_label']


class GroupSerializer(serializers.ModelSerializer):
    permission_ids = serializers.PrimaryKeyRelatedField(
        source='permissions', queryset=Permission.objects.all(), many=True, required=False
    )
    permissions_detail = PermissionSerializer(source='permissions', many=True, read_only=True)
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'permission_ids', 'permissions_detail', 'user_count']

    def get_user_count(self, obj):
        UserModel = get_user_model()
        return UserModel.objects.filter(groups=obj).count()

    def create(self, validated_data):
        permissions = validated_data.pop('permissions', [])
        group = super().create(validated_data)
        group.permissions.set(permissions)
        return group

    def update(self, instance, validated_data):
        permissions = validated_data.pop('permissions', None)
        instance = super().update(instance, validated_data)
        if permissions is not None:
            instance.permissions.set(permissions)
        return instance


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False, write_only=True)
    group_ids = serializers.PrimaryKeyRelatedField(
        source='groups', queryset=Group.objects.all(), many=True, required=False
    )
    group_names = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='')

    class Meta:
        model = User
        fields = [
            'id', 'username', 'phone_number', 'avatar', 'dd_user_id', 'password',
            'is_staff', 'is_active', 'is_superuser',
            'create_time', 'update_time', 'created_by', 'updated_by', 'created_by_name',
            'group_ids', 'group_names',
        ]

    def get_group_names(self, obj):
        return list(obj.groups.values_list('name', flat=True))

    def _is_superuser_request(self):
        """判断当前请求者是否为超级管理员"""
        request = self.context.get('request')
        return bool(request and request.user and request.user.is_superuser)

    def validate_phone_number(self, value):
        if not PHONE_RE.match(value):
            raise serializers.ValidationError('手机号格式不正确')
        qs = User.objects.filter(phone_number=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('该手机号已被注册')
        return value

    def validate_password(self, value):
        if value and len(value) < 6:
            raise serializers.ValidationError('密码长度不能少于6位')
        return value

    def create(self, validated_data):
        # 非超级管理员不允许设置 is_staff / is_superuser
        if not self._is_superuser_request():
            validated_data.pop('is_staff', None)
            validated_data.pop('is_superuser', None)
        groups = validated_data.pop('groups', [])
        password = validated_data.pop('password', None)
        is_default = password is None
        validated_data['password'] = make_password(password or 'Test123456')
        user = super().create(validated_data)
        user.groups.set(groups)
        if is_default:
            user.is_default_password = True
            user.save(update_fields=['is_default_password'])
        return user

    def update(self, instance, validated_data):
        # 非超级管理员不允许修改 is_staff / is_superuser
        if not self._is_superuser_request():
            validated_data.pop('is_staff', None)
            validated_data.pop('is_superuser', None)
        groups = validated_data.pop('groups', None)
        password = validated_data.pop('password', None)
        if password:
            validated_data['password'] = make_password(password)
            validated_data['is_default_password'] = False
        instance = super().update(instance, validated_data)
        if groups is not None:
            instance.groups.set(groups)
        return instance


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
