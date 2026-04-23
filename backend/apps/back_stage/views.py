from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from .models import User
from .serializers import UserSerializer, UserMeSerializer, GroupSerializer
from .filters import UserFilter
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from .permissions import IsSuperUser, CanModifyUser
from apps.common_views.response import APIResponse
from apps.common_views.views import BaseModelViewSet
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.decorators import action
from django.contrib.auth.models import Group, Permission


class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all().order_by('-create_time')
    serializer_class = UserSerializer

    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]

        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [CanModifyUser()]

        return [IsAuthenticated()]

    def perform_destroy(self, instance):
        # 显式清理 M2M 关联，避免 MySQL 外键约束与 ORM collector 顺序冲突
        instance.groups.clear()
        instance.user_permissions.clear()
        instance.delete()


# 只暴露业务 app 的权限，过滤掉 Django 内置 app
BUSINESS_APPS = {'back_stage', 'version_pack', 'common_views', 'data_manage'}


class GroupViewSet(ModelViewSet):
    """角色（权限组）管理"""
    queryset = Group.objects.all().order_by('id')
    serializer_class = GroupSerializer

    def get_permissions(self):
        # list/retrieve：is_staff 或以上可查看（供用户管理弹窗加载角色选项）
        # create/update/destroy：仅超级管理员
        if self.action in ['list', 'retrieve']:
            return [CanModifyUser()]
        return [IsSuperUser()]

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def all_permissions(self, request):
        """返回业务相关权限，用于前端选择器"""
        perms = Permission.objects.select_related('content_type').filter(
            content_type__app_label__in=BUSINESS_APPS
        ).order_by('content_type__app_label', 'codename')
        data = [
            {
                'id': p.id,
                'name': p.name,
                'codename': p.codename,
                'app_label': p.content_type.app_label,
            }
            for p in perms
        ]
        return Response(data)



class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get('phone_number')
        password = request.data.get('password')

        if not phone or not password:
            return APIResponse(msg="手机号和密码不能为空", code=1001, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, phone_number=phone, password=password)

        if user is None:
            return APIResponse(msg="手机号或密码错误", code=1002, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return APIResponse(msg="用户已被禁用", code=1003, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)

        return APIResponse(data={
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserMeSerializer(user).data
        })


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        old_pwd = request.data.get('old_password')
        new_pwd = request.data.get('new_password')

        if not old_pwd or not new_pwd:
            return APIResponse(msg="参数不完整", code=1001, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_pwd):
            return APIResponse(msg="旧密码错误", code=1002, status=status.HTTP_400_BAD_REQUEST)

        if old_pwd == new_pwd:
            return APIResponse(msg="新密码不能和旧密码相同", code=1003, status=status.HTTP_400_BAD_REQUEST)

        if len(new_pwd) < 6:
            return APIResponse(msg="密码至少6位", code=1004, status=status.HTTP_400_BAD_REQUEST)

        # 设置新密码
        user.set_password(new_pwd)
        user.save()

        return APIResponse(msg="密码修改成功，请重新登录")
