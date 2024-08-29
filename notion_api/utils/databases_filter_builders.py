from abc import ABC, abstractmethod


class BaseFilterBuilder(ABC):
    def __init__(self, property_name):
        self.property_name = property_name
        self.filter_type = self.__class__.__name__.lower().replace("filterbuilder", "")

    @abstractmethod
    def build(self):
        pass


class NumberFilterBuilder(BaseFilterBuilder):
    def equals(self, value):
        self.condition = {"equals": value}
        return self

    def does_not_equal(self, value):
        self.condition = {"does_not_equal": value}
        return self

    def greater_than(self, value):
        self.condition = {"greater_than": value}
        return self

    def less_than(self, value):
        self.condition = {"less_than": value}
        return self

    def greater_than_or_equal_to(self, value):
        self.condition = {"greater_than_or_equal_to": value}
        return self

    def less_than_or_equal_to(self, value):
        self.condition = {"less_than_or_equal_to": value}
        return self

    def build(self):
        return {"property": self.property_name, self.filter_type: self.condition}


class TextFilterBuilder(BaseFilterBuilder):
    def equals(self, value):
        self.condition = {"equals": value}
        return self

    def does_not_equal(self, value):
        self.condition = {"does_not_equal": value}
        return self

    def contains(self, value):
        self.condition = {"contains": value}
        return self

    def does_not_contain(self, value):
        self.condition = {"does_not_contain": value}
        return self

    def starts_with(self, value):
        self.condition = {"starts_with": value}
        return self

    def ends_with(self, value):
        self.condition = {"ends_with": value}
        return self

    def build(self):
        return {"property": self.property_name, "rich_text": self.condition}


class SelectFilterBuilder(BaseFilterBuilder):
    def equals(self, value):
        self.condition = {"equals": value}
        return self

    def does_not_equal(self, value):
        self.condition = {"does_not_equal": value}
        return self

    def is_empty(self):
        self.condition = {"is_empty": True}
        return self

    def is_not_empty(self):
        self.condition = {"is_not_empty": True}
        return self

    def build(self):
        return {"property": self.property_name, self.filter_type: self.condition}


class MultiSelectFilterBuilder(BaseFilterBuilder):
    def contains(self, value):
        self.condition = {"contains": value}
        return self

    def does_not_contain(self, value):
        self.condition = {"does_not_contain": value}
        return self

    def is_empty(self):
        self.condition = {"is_empty": True}
        return self

    def is_not_empty(self):
        self.condition = {"is_not_empty": True}
        return self

    def build(self):
        return {"property": self.property_name, self.filter_type: self.condition}


class DateFilterBuilder(BaseFilterBuilder):
    def equals(self, value):
        self.condition = {"equals": value}
        return self

    def before(self, value):
        self.condition = {"before": value}
        return self

    def after(self, value):
        self.condition = {"after": value}
        return self

    def on_or_before(self, value):
        self.condition = {"on_or_before": value}
        return self

    def on_or_after(self, value):
        self.condition = {"on_or_after": value}
        return self

    def is_empty(self):
        self.condition = {"is_empty": True}
        return self

    def is_not_empty(self):
        self.condition = {"is_not_empty": True}
        return self

    def build(self):
        return {"property": self.property_name, self.filter_type: self.condition}


class CheckboxFilterBuilder(BaseFilterBuilder):
    def equals(self, value):
        self.condition = {"equals": value}
        return self

    def does_not_equal(self, value):
        self.condition = {"does_not_equal": value}
        return self

    def build(self):
        return {"property": self.property_name, self.filter_type: self.condition}


class FilterComposer:
    def __init__(self):
        self.filters = []

    def add_filter(self, filter_dict):
        self.filters.append(filter_dict)
        return self

    def build(self, operator="and"):
        if len(self.filters) == 1:
            return {"filter": self.filters[0]}
        else:
            return {"filter": {operator: self.filters}}
