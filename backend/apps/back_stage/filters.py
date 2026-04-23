import django_filters
from apps.back_stage.models import User


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(lookup_expr='icontains')
    phone_number = django_filters.CharFilter(lookup_expr='icontains')
    dd_user_id = django_filters.CharFilter(lookup_expr='icontains')
    is_staff = django_filters.BooleanFilter()
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = User
        fields = ['username', 'phone_number', 'dd_user_id', 'is_staff', 'is_active']
