import django_filters
from apps.sim_test_get.models import GetTestTarget, AgvBody, GetTestCommonParameter


class GetTestTargetFilter(django_filters.FilterSet):
    target_name = django_filters.CharFilter(lookup_expr='icontains')
    model_name = django_filters.CharFilter(lookup_expr='icontains')
    target_type = django_filters.CharFilter(lookup_expr='exact')
    create_time_after = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = GetTestTarget
        fields = ['target_name', 'model_name', 'target_type', 'created_by']


class AgvBodyFilter(django_filters.FilterSet):
    agv_type = django_filters.CharFilter(lookup_expr='icontains')
    create_time_after = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = AgvBody
        fields = ['agv_type', 'created_by']


class GetTestCommonParameterFilter(django_filters.FilterSet):
    common_parameter_name = django_filters.CharFilter(lookup_expr='icontains')
    sim_test_version = django_filters.CharFilter(lookup_expr='exact')
    sim_test_vehicle = django_filters.CharFilter(lookup_expr='exact')
    create_time_after = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = GetTestCommonParameter
        fields = ['common_parameter_name', 'sim_test_version', 'sim_test_vehicle', 'created_by']
