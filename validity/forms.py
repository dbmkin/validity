from dcim.models import DeviceType, Location, Manufacturer, Platform, Site
from extras.models import Tag
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelMultipleChoiceField
from django.forms.fields import CharField

from validity import models
from django.forms import PasswordInput


class ComplianceTestForm(NetBoxModelForm):
    selectors = DynamicModelMultipleChoiceField(queryset=models.ComplianceSelector.objects.all())

    class Meta:
        model = models.ComplianceTest
        fields = ("name", "expression", "selectors", "tags")


class ComplianceSelectorForm(NetBoxModelForm):
    tags_filter = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)
    manufacturer_filter = DynamicModelMultipleChoiceField(queryset=Manufacturer.objects.all(), required=False)
    type_filter = DynamicModelMultipleChoiceField(queryset=DeviceType.objects.all(), required=False)
    platform_filter = DynamicModelMultipleChoiceField(queryset=Platform.objects.all(), required=False)
    location_filter = DynamicModelMultipleChoiceField(queryset=Location.objects.all(), required=False)
    site_filter = DynamicModelMultipleChoiceField(queryset=Site.objects.all(), required=False)

    class Meta:
        model = models.ComplianceSelector
        fields = (
            "name",
            "filter_operation",
            "dynamic_pairs",
            "name_filter",
            "tags_filter",
            "manufacturer_filter",
            "type_filter",
            "platform_filter",
            "status_filter",
            "location_filter",
            "site_filter",
            "tags",
        )


class GitRepoForm(NetBoxModelForm):
    password = CharField(widget=PasswordInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['password'].disabled = True

    class Meta:
        model = models.GitRepo
        fields = ("name", "repo_url", "default_device_path", "default", "username", "password", "tags")

    def save(self, commit: bool = ...):
        self.instance.password = self.cleaned_data['password']
        return super().save(commit)


class ConfigSerializerForm(NetBoxModelForm):
    class Meta:
        model = models.ConfigSerializer
        fields = ('name', 'ttp_template', 'tags')
