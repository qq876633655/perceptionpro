from rest_framework.permissions import BasePermission


class IsDevRole(BasePermission):
    """超级管理员 或 dev 组成员"""
    def has_permission(self, request, view):
        user = request.user

        if user.is_superuser:
            return True

        return user.groups.filter(name='dev').exists()


class IsSuperUser(BasePermission):
    """只有超级管理员可以操作"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class CanModifyUser(BasePermission):
    """
    用户增删改权限：
    - 超级管理员：可操作所有用户
    - 管理员 (is_staff)：可操作非超级管理员用户
    - 普通用户：无操作权限
    """
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            (request.user.is_superuser or request.user.is_staff)
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        # 管理员不能修改/删除超级管理员
        return not obj.is_superuser


class HasModelPermission(BasePermission):
    """
    基于 Django Model 权限控制版本/环境资源：
    - 超级管理员：无限制
    - 其他用户（含管理员）：需要角色分配的模型权限
        list/retrieve/creators → view_<model>
        create               → add_<model>
        update/partial_update → change_<model>
        destroy/batch_delete  → delete_<model>
    """

    _action_to_perm = {
        'list':           'view',
        'retrieve':       'view',
        'creators':       'view',
        'create':         'add',
        'update':         'change',
        'partial_update': 'change',
        'destroy':        'delete',
        'batch_delete':   'delete',
    }

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        action = getattr(view, 'action', None)
        perm_type = self._action_to_perm.get(action)
        if perm_type is None:
            return True  # 未知 action 默认放行

        qs = getattr(view, 'queryset', None)
        if qs is None:
            return True

        model = qs.model
        perm = f'{model._meta.app_label}.{perm_type}_{model._meta.model_name}'
        return request.user.has_perm(perm)
