from django.contrib.auth.backends import ModelBackend
from apps.back_stage.models import User


class PhoneBackend(ModelBackend):
    """
    使用手机号登录
    """

    def authenticate(self, request, username=None, password=None, phone_number=None, **kwargs):
        # 🔥 兼容写法：有些地方仍传 username
        phone = phone_number or username

        if phone is None or password is None:
            return None

        try:
            user = User.objects.get(phone_number=phone)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None