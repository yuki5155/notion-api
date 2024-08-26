# abstract class for ORM
from abc import ABC, abstractmethod


class models(ABC):
    pass


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

    def save(self):
        pass

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
    def migrate(cls):
        fields = [v for v in vars(cls).values() if isinstance(v, BaseField)]
        for field in fields:
            print(
                f"{field} (クラス名: {field.__class__.__name__}, Required: {field.is_required})"
            )
        print(f"Table name: {cls.table_name()}")


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


class IntegerField(BaseField):
    def __init__(self, record_name, is_required=False):
        super().__init__(record_name, is_required)

    def run(self, value):
        if value is None and not self.is_required:
            return None
        if not isinstance(value, int):
            raise ValueError(f"{self.record_name} must be an integer")
        return value


if __name__ == "__main__":

    class TestModel(Model):
        title = CharField("タイトル", is_required=True)
        content = CharField("content")
        number = IntegerField("number")

        @classmethod
        def table_name(cls):
            return "test_model"

    # Test migrate without initialization
    print("Test: Migrate without initialization")
    TestModel.migrate()

    # Test with correct field names
    test1 = TestModel(title="test1", content="test content", number=1)
    print(f"Test1: {test1}")
    assert test1.is_valid()

    # Test with missing optional fields
    test2 = TestModel(title="test2")
    print(f"Test2: {test2}")
    assert test2.is_valid()

    # Test missing required field
    try:
        TestModel(content="no title")
    except ValueError as e:
        print(f"ValueError raised as expected: {e}")

    # Test invalid field
    try:
        TestModel(title="test", invalid_field="invalid")
    except AttributeError as e:
        print(f"AttributeError raised as expected: {e}")

    print("All tests passed successfully!")
