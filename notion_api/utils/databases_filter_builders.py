from typing import List, Dict, Any
from abc import ABC, abstractmethod


class FilterComposer:
    def __init__(self):
        self.filters: List[Dict[str, Any]] = []

    def add_filter(self, filter_dict: Dict[str, Any]) -> "FilterComposer":
        self.filters.append(filter_dict)
        return self

    def build(self, operator: str = "and") -> Dict[str, Any]:
        if len(self.filters) == 0:
            return {}
        elif len(self.filters) == 1:
            return {"filter": self.filters[0]}
        else:
            return {"filter": {operator: self.filters}}


class BaseFilterBuilder(ABC):
    def __init__(self, property_name):
        self.property_name = property_name
        self.condition = {}

    @abstractmethod
    def build(self):
        pass

    def _add_condition(self, condition_name, value):
        self.condition[condition_name] = value
        return self


class NumberFilterBuilder(BaseFilterBuilder):
    def does_not_equal(self, value):
        return self._add_condition("does_not_equal", value)

    def equals(self, value):
        return self._add_condition("equals", value)

    def greater_than(self, value):
        return self._add_condition("greater_than", value)

    def greater_than_or_equal_to(self, value):
        return self._add_condition("greater_than_or_equal_to", value)

    def less_than(self, value):
        return self._add_condition("less_than", value)

    def less_than_or_equal_to(self, value):
        return self._add_condition("less_than_or_equal_to", value)

    def is_empty(self):
        return self._add_condition("is_empty", True)

    def is_not_empty(self):
        return self._add_condition("is_not_empty", True)

    def build(self):
        return {"property": self.property_name, "number": self.condition}
