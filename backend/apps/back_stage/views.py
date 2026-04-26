import logging

from common.dd_no_login import DDNoLogin
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect
from django.core.files.storage import default_storage
from urllib.parse import urlencode
from django_filters.rest_framework import DjangoFilterBackend
from common.dd_robot import dd_h5_robot
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
import config.perceptionpro_cfg as ppc

audit_log = logging.getLogger('apps.audit')


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
        super().perform_destroy(instance)


# 只暴露业务 app 的权限，过滤掉 Django 内置 app
BUSINESS_APPS = {'back_stage', 'version_pack', 'common_views', 'data_manage', 'sim_test_agv', 'sim_test_get'}


class GroupViewSet(ModelViewSet):
    """角色（权限组）管理"""
    queryset = Group.objects.all().order_by('id')
    serializer_class = GroupSerializer

    def get_permissions(self):
        # list/retrieve：所有登录用户可查看角色名（供申请权限弹窗使用）
        # create/update/destroy：仅超级管理员
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
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

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
        ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR', '-')
        if user is None:
            audit_log.warning('登录失败 手机号=%s IP=%s', phone, ip)
            return APIResponse(msg="手机号或密码错误", code=1002, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            audit_log.warning('登录失败(已禁用) 用户=%s IP=%s', user.username, ip)
            return APIResponse(msg="用户已被禁用", code=1003, status=status.HTTP_400_BAD_REQUEST)

        audit_log.info('登录成功 用户=%s IP=%s', user.username, ip)
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
        user.is_default_password = False
        user.save()

        return APIResponse(msg="密码修改成功，请重新登录")


def dd_login(request):
    # hostname = request.get_host().split(":")[0]
    # frontend_url = f"http://{hostname}:5173"
    frontend_url = ppc.PER_PRO_LOCAL_SERVER_URL

    authcode = request.GET.get("authCode")
    get_code = request.GET.get("code")

    try:
        dd = DDNoLogin()
        if authcode is not None:
            union_id = dd.dd_login(authcode)
            user_info = dd.user_info(union_id=union_id)
        else:
            user_info = dd.user_info(corp_id=get_code)
    except Exception as e:
        params = urlencode({"error": f"钉钉验证失败：{e}"})
        return HttpResponseRedirect(f"{frontend_url}/login?{params}")

    user = User.objects.filter(phone_number=user_info["phone_number"]).first()
    if user is None:
        user = User.objects.create_user(
            username=user_info["username"],
            phone_number=user_info["phone_number"],
            dd_user_id=user_info["dd_user_id"],
            avatar=user_info.get("avatar", ""),
            is_staff=False,
            is_superuser=False,
            is_active=True,
            is_default_password=True,
            password='Test123456',
        )
        # 分配默认角色 visitor
        visitor_group = Group.objects.filter(name='visitor').first()
        if visitor_group:
            user.groups.add(visitor_group)

    refresh = RefreshToken.for_user(user)
    params = urlencode({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    })
    return HttpResponseRedirect(f"{frontend_url}/dd-callback?{params}")


class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]

    MAX_SIZE = 3 * 1024 * 1024  # 3 MB

    def post(self, request):
        file = request.FILES.get('avatar')
        if not file:
            return APIResponse(msg="请选择文件", code=1001, status=status.HTTP_400_BAD_REQUEST)

        if file.size > self.MAX_SIZE:
            return APIResponse(msg="图片不能超过 3MB", code=1002, status=status.HTTP_400_BAD_REQUEST)

        if not file.content_type.startswith('image/'):
            return APIResponse(msg="只允许上传图片文件", code=1003, status=status.HTTP_400_BAD_REQUEST)

        ext = file.name.rsplit('.', 1)[-1].lower()
        save_path = f"avatar/{request.user.pk}.{ext}"
        # 如有旧头像文件则删除
        if default_storage.exists(save_path):
            default_storage.delete(save_path)
        default_storage.save(save_path, file)

        avatar_url = request.build_absolute_uri(f"/media/{save_path}")
        request.user.avatar = avatar_url
        request.user.save(update_fields=['avatar'])

        return APIResponse(data={"avatar": avatar_url})


class RoleRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        department = request.data.get('department', '').strip()
        role_names = request.data.get('roles', [])

        if not department:
            return APIResponse(msg="请填写部门", code=1001, status=status.HTTP_400_BAD_REQUEST)
        if not role_names:
            return APIResponse(msg="请选择申请的角色", code=1002, status=status.HTTP_400_BAD_REQUEST)

        # 查找所有管理员中有 dd_user_id 的用户
        admin_user_ids = list(
            User.objects.filter(is_staff=True, dd_user_id__isnull=False)
            .exclude(dd_user_id='')
            .values_list('dd_user_id', flat=True)
        )

        if admin_user_ids:
            roles_str = '、'.join(role_names)
            msg = {
                'content': (
                    f"【权限申请】\n"
                    f"用户：{request.user.username}\n"
                    f"手机号：{request.user.phone_number}\n"
                    f"部门：{department}\n"
                    f"申请角色：{roles_str}\n"
                    f"请登录平台在用户管理中处理。"
                )
            }
            try:
                dd_h5_robot(admin_user_ids, msg)
            except Exception:
                pass  # 通知失败不影响主流程

        # 将用户的部门信息更新到模型
        if department:
            request.user.department = department
            request.user.save(update_fields=['department'])

        return APIResponse(msg="申请已提交，请等待管理员审核")