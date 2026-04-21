from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, MeView, LoginView, ChangePasswordView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),

    # 👇 自定义接口统一放这里
    path('me/', MeView.as_view()),

    path('login/', LoginView.as_view()),
    path('change_pwd/', ChangePasswordView.as_view()),
]