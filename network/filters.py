import django_filters
from .models import NetworkNode


class NetworkNodeFilter(django_filters.FilterSet):
    country = django_filters.CharFilter(field_name='country', lookup_expr='iexact')
    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains')
    node_type = django_filters.ChoiceFilter(choices=NetworkNode.NODE_TYPES)
    has_debt = django_filters.BooleanFilter(method='filter_has_debt')
    supplier = django_filters.ModelChoiceFilter(queryset=NetworkNode.objects.all())
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = NetworkNode
        fields = ['country', 'city', 'node_type', 'supplier', 'is_active']

    def filter_has_debt(self, queryset, name, value):
        if value:
            return queryset.filter(debt__gt=0)
        return queryset.filter(debt=0)
