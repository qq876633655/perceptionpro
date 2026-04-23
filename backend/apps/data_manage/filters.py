import django_filters
from apps.data_manage.models import SimProjectProperty, SimCommonProperty


class SimProjectPropertyFilter(django_filters.FilterSet):
    apply_project = django_filters.CharFilter(lookup_expr='icontains')
    property_tag = django_filters.CharFilter(lookup_expr='icontains')
    create_time_after = django_filters.DateTimeFilter(field_name="create_time", lookup_expr='gte')
    create_time_before = django_filters.DateTimeFilter(field_name="create_time", lookup_expr='lte')

    class Meta:
        model = SimProjectProperty
        fields = ['apply_project', 'property_tag', 'created_by']


class SimCommonPropertyFilter(django_filters.FilterSet):
    property_tag = django_filters.CharFilter(lookup_expr='icontains')
    create_time_after = django_filters.DateTimeFilter(field_name="create_time", lookup_expr='gte')
    create_time_before = django_filters.DateTimeFilter(field_name="create_time", lookup_expr='lte')

    class Meta:
        model = SimCommonProperty
        fields = ['property_tag', 'created_by']
