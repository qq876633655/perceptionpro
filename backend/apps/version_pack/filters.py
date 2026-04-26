import django_filters
from apps.version_pack.models import PerEnv, PerVersion, LocEnv, LocVersion, CtlEnv, CtlVersion, SimEnv, SimVersion, SenEnv, SenVersion, AtEnv, AtVersion


def make_env_filter(model_cls):
    class _EnvFilter(django_filters.FilterSet):
        create_time_after = django_filters.DateTimeFilter(field_name="create_time", lookup_expr='gte')
        create_time_before = django_filters.DateTimeFilter(field_name="create_time", lookup_expr='lte')
        class Meta:
            model = model_cls
            fields = ['apply_project', 'created_by']
    _EnvFilter.__name__ = f'{model_cls.__name__}Filter'
    return _EnvFilter


def make_version_filter(model_cls):
    class _VersionFilter(django_filters.FilterSet):
        versions_type = django_filters.CharFilter(method='filter_versions_type')
        create_time_after = django_filters.DateTimeFilter(field_name="create_time", lookup_expr='gte')
        create_time_before = django_filters.DateTimeFilter(field_name="create_time", lookup_expr='lte')
        def filter_versions_type(self, queryset, name, value):
            return queryset.filter(versions_type__contains=value)
        class Meta:
            model = model_cls
            fields = ['versions_type', 'apply_project', 'env', 'test_result', 'created_by']
    _VersionFilter.__name__ = f'{model_cls.__name__}Filter'
    return _VersionFilter


PerEnvFilter     = make_env_filter(PerEnv)
PerVersionFilter = make_version_filter(PerVersion)

LocEnvFilter     = make_env_filter(LocEnv)
LocVersionFilter = make_version_filter(LocVersion)

CtlEnvFilter     = make_env_filter(CtlEnv)
CtlVersionFilter = make_version_filter(CtlVersion)

SimEnvFilter     = make_env_filter(SimEnv)
SimVersionFilter = make_version_filter(SimVersion)

SenEnvFilter     = make_env_filter(SenEnv)
SenVersionFilter = make_version_filter(SenVersion)

AtEnvFilter     = make_env_filter(AtEnv)
AtVersionFilter = make_version_filter(AtVersion)