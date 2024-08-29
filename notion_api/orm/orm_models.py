from abc import ABC, abstractmethod
from .fields import (
    BaseField,
    CharField,
    IntegerField,
    SelectField,
    MultiSelectField,
    DateField,
    BoolField,
)
from notion_api.domains.databases_domain import DatabaseTitle
from notion_api.services.v1.databases import DataBaseService
from notion_api.utils.database_record_ops import DatabaseRecord


class Model:
    def __init__(self, **kwargs):
        # Create a mapping of record_name to field_name and vice versa
        self._field_mapping = {}
        self._reverse_mapping = {}
        for field_name, field in vars(self.__class__).items():
            if isinstance(field, BaseField):
                self._field_mapping[field.record_name] = field_name
                self._reverse_mapping[field_name] = field.record_name

        # Check for invalid fields
        invalid_fields = [
            key
            for key in kwargs
            if key not in self._field_mapping and key not in self._reverse_mapping
        ]
        if invalid_fields:
            raise AttributeError(f"Invalid fields: {', '.join(invalid_fields)}")

        # Check for missing required fields
        required_fields = [
            field_name
            for field_name, field in vars(self.__class__).items()
            if isinstance(field, BaseField) and field.is_required
        ]
        missing_fields = [field for field in required_fields if field not in kwargs]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        for key, value in kwargs.items():
            field_name = self._field_mapping.get(key, key)
            if hasattr(self.__class__, field_name):
                field = getattr(self.__class__, field_name)
                if isinstance(field, BaseField):
                    setattr(self, field_name, field.run(value))
                else:
                    setattr(self, field_name, value)

    def is_valid(self):
        fields = [v for v in vars(self.__class__).values() if isinstance(v, BaseField)]
        for field in fields:
            field_name = self._field_mapping.get(field.record_name, field.record_name)
            if field.is_required and getattr(self, field_name) is None:
                return False
        return True

    def save(self, database_id):
        if not self.is_valid():
            raise ValueError("Invalid model")
        d = DataBaseService()
        record = DatabaseRecord(database_id)

        # Add "Name" property as title
        title_field = next(
            (
                f
                for f in vars(self.__class__).values()
                if isinstance(f, BaseField) and f.record_name == "Name"
            ),
            None,
        )
        if title_field:
            title_value = getattr(
                self, self._field_mapping.get("Name", "Name"), str(self)
            )
        else:
            title_value = (
                f"{self.__class__.__name__}_{id(self)}"  # デフォルトのタイトル
            )
        record.add_property("Name", title_value, CharField("Name"))

        for field_name, field in vars(self.__class__).items():
            if isinstance(field, BaseField) and field.record_name != "Name":
                value = getattr(self, field_name)
                record.add_property(field.record_name, value, field)

        new_record = d.insert_record(database_id, record.to_dict())
        return new_record

    def __str__(self):
        title_field = next(
            (
                f
                for f in vars(self.__class__).values()
                if isinstance(f, BaseField) and f.record_name == "タイトル"
            ),
            None,
        )
        if title_field:
            field_name = self._field_mapping.get("タイトル", "タイトル")
            return getattr(self, field_name, f"<{self.__class__.__name__}>")
        return f"<{self.__class__.__name__}>"

    @classmethod
    @abstractmethod
    def table_name(cls):
        pass

    @classmethod
    def choose_field(cls, field):
        if field.__class__.__name__ == CharField.__name__:
            return {"rich_text": {}}
        elif field.__class__.__name__ == IntegerField.__name__:
            return {"number": {}}
        elif field.__class__.__name__ == SelectField.__name__:
            return {"select": {"options": field.options}}
        elif field.__class__.__name__ == MultiSelectField.__name__:
            return {"multi_select": {"options": field.options}}
        elif field.__class__.__name__ == DateField.__name__:
            return {"date": {}}
        elif field.__class__.__name__ == BoolField.__name__:
            return {"checkbox": {}}
        else:
            raise ValueError(f"Invalid field type: {field.__class__.__name__}")

    @classmethod
    def migrate(cls, parent_id=None):
        db_property = {
            "Name": {"title": {}},
        }

        fields = [v for v in vars(cls).values() if isinstance(v, BaseField)]

        for field in fields:
            db_property[field.record_name] = cls.choose_field(field)

        database_title = DatabaseTitle(content=cls.table_name())
        db_service = DataBaseService()
        result = db_service.create_notion_database(
            title=database_title, parent_id=parent_id, properties=db_property
        )
        return {
            "code": 200,
            "message": f"Database {cls.table_name()} migrated successfully",
            "database_id": result["body"]["id"],
        }
