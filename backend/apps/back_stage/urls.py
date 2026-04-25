from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, GroupViewSet, MeView, LoginView, ChangePasswordView, AvatarUploadView, RoleRequestView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'groups', GroupViewSet, basename='groups')

urlpatterns = [
    path('', include(router.urls)),

    # 👇 自定义接口统一放这里
    path('me/', MeView.as_view()),

    path('login/', LoginView.as_view()),
    path('change_pwd/', ChangePasswordView.as_view()),
    path('avatar/', AvatarUploadView.as_view()),
    path('role_request/', RoleRequestView.as_view()),
]
