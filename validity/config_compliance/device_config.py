from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import ClassVar

from dcim.models import Device
from django.utils.timezone import make_aware
from ttp import ttp

from validity import settings
from .exceptions import DeviceConfigError


@dataclass
class TTPTemplate:
    name: str
    template: str = ""  # according to TTP API this may contain a template iteslf or a filepath


@dataclass
class DeviceConfig:
    device: Device
    config_path: Path
    last_modified: datetime | None = None
    template: TTPTemplate | None = None
    serialized: dict | list | None = None
    _git_folder: ClassVar[Path] = settings.git_folder

    @classmethod
    def _full_config_path(cls, device: Device) -> Path:
        return cls._git_folder / device.repo.name / device.repo.rendered_device_path(device)

    @classmethod
    def from_device(cls, device: Device) -> "DeviceConfig":
        """
        Get DeviceConfig from dcim.models.Device
        Device MUST be annotated with ".git_repo" pointing to a repo with device config file
        Device MUST be annotated with ".serializer" pointing to appropriate config serializer instance
        """
        assert hasattr(device, "repo"), "Device must be annotated with .repo"
        assert hasattr(device, "serializer"), "Device must be annotated with .serializer"
        try:
            device_path = cls._full_config_path(device)
            last_modified = None
            if device_path.is_file():
                lm_timestamp = device_path.stat().st_mtime
                last_modified = make_aware(datetime.fromtimestamp(lm_timestamp))
            template = TTPTemplate(name=device.serializer.name, template=device.serializer.effective_template)
            return cls(device, device_path, last_modified, template)
        except AttributeError as e:
            raise DeviceConfigError(str(e)) from e

    def serialize(self) -> None:
        serialize_configs(self, override=True)


def serialize_configs(*configs: DeviceConfig, override: bool = False) -> None:
    parser = ttp()
    configs_by_template = defaultdict(list)
    templates = {}
    for config in configs:
        if config.template:
            configs_by_template[config.template.name].append(config)
            templates.setdefault(config.template.name, config.template.template)
    for template_name, config_group in configs_by_template.items():
        parser.add_template(template=templates[template_name], template_name=template_name)
        for config in config_group:
            parser.add_input(data=str(config.config_path.absolute()), template_name=template_name)
    parser.parse()
    for template_name, config_group in configs_by_template.items():
        result = parser.result(templates=[template_name])[0]
        for config, serialized in zip(config_group, result):
            if override or config.serialized is not None:
                config.serialized = serialized
