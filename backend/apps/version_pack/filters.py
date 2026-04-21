import django_filters
from apps.version_pack.models import PerVersion


class PerVersionFilter(django_filters.FilterSet):
    versions_type = django_filters.CharFilter(method='filter_versions_type')

    def filter_versions_type(self, queryset, name, value):
        return queryset.filter(versions_type__contains=value)

    create_time_after = django_filters.DateTimeFilter(
        field_name="create_time",
        lookup_expr='gte'
    )
    create_time_before = django_filters.DateTimeFilter(
        field_name="create_time",
        lookup_expr='lte'
    )

    class Meta:
        model = PerVersion
        fields = [
            'versions_type',
            'apply_project',
            'env',
            'test_result',
            'created_by',
        ]