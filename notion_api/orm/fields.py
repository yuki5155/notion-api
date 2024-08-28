import random
from abc import ABC, abstractmethod


class BaseField:
    def __init__(self, record_name, is_required=False):
        self.record_name = record_name
        self.is_required = is_required

    def __str__(self):
        return self.record_name

    @abstractmethod
    def run(self, value):
        pass


class CharField(BaseField):
    def __init__(self, record_name, max_length=1000, is_required=False):
        super().__init__(record_name, is_required)
        self.max_length = max_length

    def run(self, value):
        if value is None and not self.is_required:
            return None
        if not isinstance(value, str):
            raise ValueError(f"{self.record_name} must be a string")
        if len(value) > self.max_length:
            raise ValueError(f"Length of {self.record_name} is too long")
        return value


class SelectField(BaseField):
    def __init__(self, record_name, options, is_required=False):
        super().__init__(record_name, is_required)
        if not options:
            raise ValueError("Options must be provided")
        if not isinstance(options, list):
            raise ValueError("Options must be a list")
        if not all(isinstance(option, dict) for option in options):
            raise ValueError("Options must be a list of dictionaries")

        self.options = options

    @classmethod
    def option(cls, name, color=None):
        color_list = [
            "default",
            "gray",
            "brown",
            "orange",
            "yellow",
            "green",
            "blue",
            "purple",
            "pink",
            "red",
        ]
        if color is None:
            color = color_list[random.randint(0, len(color_list) - 1)]
        if color not in color_list:
            raise ValueError(f"Color must be one of {color_list}")
        return {"name": name, "color": color}

    def run(self, value):
        if value is None and not self.is_required:
            return None
        if value not in self.options:
            raise ValueError(f"{self.record_name} must be one of {self.options}")
        return value


class IntegerField(BaseField):
    def __init__(self, record_name, is_required=False):
        super().__init__(record_name, is_required)

    def run(self, value):
        if value is None and not self.is_required:
            return None
        if not isinstance(value, int):
            raise ValueError(f"{self.record_name} must be an integer")
        return value
