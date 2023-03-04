import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from dcim.models import Device
from django.db.models import Q

from validity.choices import DynamicPairsChoices


if TYPE_CHECKING:
    from validity.models import ComplianceSelector


@dataclass
class DynamicPairFilter(ABC):
    selector: "ComplianceSelector"
    device: Device

    @property
    @abstractmethod
    def filter(self) -> Q | None:
        pass


class NoneFilter(DynamicPairFilter):
    @property
    def filter(self) -> None:
        return


@dataclass
class DynamicNamePairFilter(DynamicPairFilter):
    @staticmethod
    def extract_first_group(regex: str) -> str | None:
        regex = regex.replace(r"\(", "").replace(r"\)", "")
        open_bracket_index = -1
        for i, char in enumerate(regex):
            if len(regex) - i >= 3 and regex[i : i + 3] == "(?:":
                continue
            if char == "(":
                open_bracket_index = i
            if char == ")" and open_bracket_index != -1:
                return regex[open_bracket_index : i + 1]
        return None

    @property
    def filter(self) -> Q | None:
        if not self.device.name:
            return
        if not (group1 := self.extract_first_group(self.selector.name_filter)):
            return
        if not (name_match := re.match(self.selector.name_filter, self.device.name)):
            return
        start, end = name_match.start(1), name_match.end(1)
        filter_string = self.device.name[:start] + group1 + self.device.name[end:]
        return Q(name__regex=filter_string)


dynamic_pair_filters = {DynamicPairsChoices.NAME: DynamicNamePairFilter}


def dpf_factory(selector: "ComplianceSelector", device: Device) -> DynamicPairFilter:
    filter_cls = dynamic_pair_filters.get(selector.dynamic_pairs, NoneFilter)
    return filter_cls(selector, device)
