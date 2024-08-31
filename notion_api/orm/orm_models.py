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
from notion_api.utils.databases_filter_builders import (
    FilterComposer,
    NumberFilterBuilder,
    TextFilterBuilder,
    SelectFilterBuilder,
    MultiSelectFilterBuilder,
    DateFilterBuilder,
    CheckboxFilterBuilder,
)


class ModelFilter:
    def __init__(self, model_class):
        self.model_class = model_class

    def filter(self, database_id, _operator="and", **kwargs):
        from notion_api.services.v1.databases import DataBaseService

        d = DataBaseService()
        filter_composer = FilterComposer()

        for field_name, conditions in kwargs.items():
            if field_name == "_operator":
                continue
            field = getattr(self.model_class, field_name, None)
            if isinstance(field, BaseField):
                filter_builder = self._get_filter_builder(field)
                for condition, value in conditions.items():
                    filter_method = getattr(filter_builder, condition, None)
                    if filter_method:
                        filter_composer.add_filter(filter_method(value).build())

        filter_params = filter_composer.build(_operator)
        filtered_records = d.filter_database_records(database_id, filter_params)

        return [
            self._create_instance_from_record(record) for record in filtered_records
        ]

    @staticmethod
    def _get_filter_builder(field):
        if isinstance(field, IntegerField):
            return NumberFilterBuilder(field.record_name)
        elif isinstance(field, CharField):
            return TextFilterBuilder(field.record_name)
        elif isinstance(field, SelectField):
            return SelectFilterBuilder(field.record_name)
        elif isinstance(field, MultiSelectField):
            return MultiSelectFilterBuilder(field.record_name)
        elif isinstance(field, DateField):
            return DateFilterBuilder(field.record_name)
        elif isinstance(field, BoolField):
            return CheckboxFilterBuilder(field.record_name)
        else:
            raise ValueError(f"Unsupported field type: {type(field)}")

    def _create_instance_from_record(self, record):
        properties = {}
        for field_name, field in vars(self.model_class).items():
            if isinstance(field, BaseField):
                record_name = field.record_name
                if record_name in record.properties:
                    prop = record.properties[record_name]
                    if isinstance(field, CharField):
                        properties[field_name] = (
                            prop["rich_text"][0]["plain_text"]
                            if prop["rich_text"]
                            else None
                        )
                    elif isinstance(field, IntegerField):
                        properties[field_name] = prop["number"]
                    elif isinstance(field, SelectField):
                        properties[field_name] = (
                            prop["select"]["name"] if prop["select"] else None
                        )
                    elif isinstance(field, MultiSelectField):
                        properties[field_name] = [
                            option["name"] for option in prop["multi_select"]
                        ]
                    elif isinstance(field, DateField):
                        properties[field_name] = (
                            prop["date"]["start"] if prop["date"] else None
                        )
                    elif isinstance(field, BoolField):
                        properties[field_name] = prop["checkbox"]

        instance = self.model_class(**properties)
        instance.page_id = record.id  # Store the page_id in the instance
        return instance


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
        from notion_api.services.v1.databases import DataBaseService

        d = DataBaseService()
        from notion_api.utils.database_record_ops import DatabaseRecord

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
    def filter(cls, database_id, _operator="and", **kwargs):
        model_filter = ModelFilter(cls)
        return model_filter.filter(database_id, _operator=_operator, **kwargs)

    def get_page_id(self):
        return self.page_id

    def update(self, database_id, page_id=None):
        if not self.is_valid():
            raise ValueError("Invalid model")
        if page_id is None:
            page_id = self.get_page_id()
        if not page_id:
            raise ValueError("Page ID is required for update operation")
        from notion_api.services.v1.databases import DataBaseService
        from notion_api.utils.database_record_ops import DatabaseRecord

        d = DataBaseService()
        record = DatabaseRecord(database_id)

        for field_name, field in vars(self.__class__).items():
            if isinstance(field, BaseField):
                value = getattr(self, field_name)
                record.add_property(field.record_name, value, field)

        updated_record = d.update_record(page_id, record)
        return updated_record

    def get_page_id(self):
        return getattr(self, "page_id", None)

    def delete(self):
        if not hasattr(self, "page_id") or not self.page_id:
            raise ValueError("Cannot delete a record without a page_id")

        from notion_api.services.v1.databases import DataBaseService

        d = DataBaseService()

        deleted_record = d.delete_record(self.page_id)

        if deleted_record["archived"]:
            # Clear the page_id after successful deletion
            self.page_id = None
            return True
        else:
            return False

    @classmethod
    def delete_by_id(cls, database_id, page_id):
        from notion_api.services.v1.databases import DataBaseService

        d = DataBaseService()

        deleted_record = d.delete_record(page_id)

        return deleted_record["archived"]

    @classmethod
    def migrate(cls, parent_id=None):
        db_property = {
            "Name": {"title": {}},
        }

        fields = [v for v in vars(cls).values() if isinstance(v, BaseField)]

        for field in fields:
            db_property[field.record_name] = cls.choose_field(field)

        database_title = DatabaseTitle(content=cls.table_name())
        from notion_api.services.v1.databases import DataBaseService

        db_service = DataBaseService()
        result = db_service.create_notion_database(
            title=database_title, parent_id=parent_id, properties=db_property
        )
        return {
            "code": 200,
            "message": f"Database {cls.table_name()} migrated successfully",
            "database_id": result["body"]["id"],
        }
