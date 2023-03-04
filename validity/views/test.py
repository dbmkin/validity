from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from netbox.views import generic
from utilities.views import register_model_view, ViewTab

from validity import filtersets, forms, models, tables, filterset_forms
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from django.views.generic import ListView


class ComplianceTestListView(generic.ObjectListView):
    queryset = models.ComplianceTest.objects.pf_latest_results().annotate(
        passed=Count("results", filter=Q(results__passed=True)),
        failed=Count("results", filter=Q(results__passed=False)),
    )

    table = tables.ComplianceTestTable
    filterset = filtersets.ComplianceTestFilterSet


@register_model_view(models.ComplianceTest)
class ComplianceTestView(generic.ObjectView):
    queryset = models.ComplianceTest.objects.pf_latest_results()

    def get_extra_context(self, request, instance):
        table = tables.ComplianceResultTable(instance.results.all())
        table.exclude += ('test',)
        table.configure(request)
        return {"result_table": table}


@register_model_view(models.ComplianceTest, 'test_results', 'results')
class TestResultView(SingleTableMixin, FilterView):
    template_name = 'validity/compliance_results.html'
    tab = ViewTab('Results')
    model = models.ComplianceTestResult
    filterset_class = filtersets.ComplianceTestResultFilterSet
    filter_form_class = filterset_forms.TestResultFilterForm
    table_class = tables.ComplianceResultTable

    def get_queryset(self):
        return models.ComplianceTestResult.objects.select_related('test', 'device').filter(test=self.kwargs['pk'])

    def get_object(self):
        return get_object_or_404(models.ComplianceTest, pk=self.kwargs['pk'])

    def get_filterform_initial(self):
        if not hasattr(self.filterset.form, 'cleaned_data'):
            return {}
        return {k: v for k, v in self.filterset.form.cleaned_data.items() if k in self.filter_form_class.base_fields}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset_form'] = self.filter_form_class(initial=self.get_filterform_initial())
        context['object'] = self.get_object()
        context['tab'] = self.tab
        return context


@register_model_view(models.ComplianceTest, "delete")
class ComplianceTestDeleteView(generic.ObjectDeleteView):
    queryset = models.ComplianceTest.objects.all()


class ComplianceTestBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ComplianceTest.objects.pf_latest_results().annotate(
        passed=Count("results", filter=Q(results__passed=True)),
        failed=Count("results", filter=Q(results__passed=False)),
    )
    filterset = filtersets.ComplianceTestFilterSet
    table = tables.ComplianceTestTable


@register_model_view(models.ComplianceTest, "edit")
class ComplianceTestEditView(generic.ObjectEditView):
    queryset = models.ComplianceTest.objects.all()
    form = forms.ComplianceTestForm
