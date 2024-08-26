# abstract class for ORM
from abc import ABC, abstractmethod


class models(ABC):
    pass


class Model:
    def __init__(self, **kwargs):
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
            if hasattr(self, key):
                field = getattr(self.__class__, key)
                setattr(self, key, field.run(value))
            else:
                raise AttributeError(f"{key} is not a valid field")

    def save(self):
        pass

    def __str__(self):
        return getattr(self, "title", f"<{self.__class__.__name__}>")

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
        content = CharField("コンテンツ")
        number = IntegerField("番号")

        @classmethod
        def table_name(cls):
            return "test_model"

    # Test migrate without initialization
    print("Test: Migrate without initialization")
    TestModel.migrate()

    test1 = TestModel(title="test", content="test", number=1)

    test2 = TestModel(title="test only")

    try:
        test3 = TestModel(content="no title")
    except ValueError as e:
        print(f"ValueError raised as expected: {e}")
