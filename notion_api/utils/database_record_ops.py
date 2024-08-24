from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union


class AbstractProperty(ABC):
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass


class NumberProperty(AbstractProperty):
    def __init__(self, value: float):
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        return {"number": self.value}


class TextProperty(AbstractProperty):
    def __init__(self, content: str):
        self.content = content

    def to_dict(self) -> Dict[str, Any]:
        return {"title": [{"text": {"content": self.content}}]}


class SelectProperty(AbstractProperty):
    def __init__(self, name: str):
        self.name = name

    def to_dict(self) -> Dict[str, Any]:
        return {"select": {"name": self.name}}


class MultiSelectProperty(AbstractProperty):
    def __init__(self, names: List[str]):
        self.names = names

    def to_dict(self) -> Dict[str, Any]:
        return {"multi_select": [{"name": name} for name in self.names]}


class DateProperty(AbstractProperty):
    def __init__(self, start: str, end: str = None):
        self.start = start
        self.end = end

    def to_dict(self) -> Dict[str, Any]:
        date_dict = {"start": self.start}
        if self.end:
            date_dict["end"] = self.end
        return {"date": date_dict}


class CheckboxProperty(AbstractProperty):
    def __init__(self, checked: bool):
        self.checked = checked

    def to_dict(self) -> Dict[str, Any]:
        return {"checkbox": self.checked}


class DatabaseProperties:
    def __init__(self):
        self.properties: Dict[str, AbstractProperty] = {}

    def add_property(self, name: str, property: AbstractProperty):
        self.properties[name] = property

    def to_dict(self) -> Dict[str, Any]:
        return {name: prop.to_dict() for name, prop in self.properties.items()}


from typing import Dict, Any, List, Union


class DatabaseRecord:
    def __init__(self, database_id: str):
        self.database_id = database_id
        self.properties = {}

    def add_property(self, name: str, value: Union[float, str, List[str], bool]):
        # in python, T/F are read as int and bool, so we need to exclude bool from int
        if isinstance(value, (float, int)) and not isinstance(value, bool):
            self.properties[name] = {"number": float(value)}
        elif isinstance(value, str):
            if name.lower() == "name" or name.lower() == "title":
                self.properties[name] = {"title": [{"text": {"content": value}}]}
            else:
                self.properties[name] = {"select": {"name": value}}
        elif isinstance(value, list):
            self.properties[name] = {"multi_select": [{"name": item} for item in value]}
        elif isinstance(value, bool):
            self.properties[name] = {"checkbox": value}
        else:
            raise ValueError(f"Unsupported property type for {name}: {type(value)}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "parent": {"database_id": self.database_id},
            "properties": self.properties,
        }
