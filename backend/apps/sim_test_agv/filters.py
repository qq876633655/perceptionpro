import django_filters
from apps.sim_test_agv.models import (
    CaseMap, CaseProperty,
    SchemeCommonParameter, CaseTemplate, AgvTestTask,
)


class CaseMapFilter(django_filters.FilterSet):
    district_name = django_filters.CharFilter(lookup_expr='icontains')
    create_time_after = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = CaseMap
        fields = ['district_name', 'created_by']


class CasePropertyFilter(django_filters.FilterSet):
    sim_test_version = django_filters.CharFilter(lookup_expr='exact')
    sim_test_vehicle = django_filters.CharFilter(lookup_expr='exact')
    sim_scheme_name = django_filters.CharFilter(lookup_expr='exact')
    test_module = django_filters.CharFilter(lookup_expr='exact')
    property_status = django_filters.CharFilter(lookup_expr='exact')
    create_time_after = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = CaseProperty
        fields = ['sim_test_version', 'sim_test_vehicle', 'sim_scheme_name',
                  'test_module', 'property_status', 'created_by']


class SchemeCommonParameterFilter(django_filters.FilterSet):
    common_parameter_name = django_filters.CharFilter(lookup_expr='icontains')
    sim_test_version = django_filters.CharFilter(lookup_expr='exact')
    sim_test_vehicle = django_filters.CharFilter(lookup_expr='exact')
    test_module = django_filters.CharFilter(lookup_expr='exact')
    common_parameter_status = django_filters.CharFilter(lookup_expr='exact')
    create_time_after = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = SchemeCommonParameter
        fields = ['sim_test_version', 'sim_test_vehicle', 'test_module',
                  'common_parameter_status', 'created_by']


class CaseTemplateFilter(django_filters.FilterSet):
    sim_test_version = django_filters.CharFilter(lookup_expr='exact')
    test_module = django_filters.CharFilter(lookup_expr='exact')
    create_time_after = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = CaseTemplate
        fields = ['sim_test_version', 'test_module', 'created_by']


class AgvTestTaskFilter(django_filters.FilterSet):
    sim_test_version = django_filters.CharFilter(lookup_expr='icontains')
    queue_name = django_filters.CharFilter(lookup_expr='icontains')
    task_status = django_filters.CharFilter(lookup_expr='exact')
    create_time_after = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')

    class Meta:
        model = AgvTestTask
        fields = ['sim_test_version', 'queue_name', 'task_status', 'created_by']
