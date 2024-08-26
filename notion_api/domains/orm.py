# abstract class for ORM
from abc import ABC, abstractmethod


class models(ABC):

    pass


class Model:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            # キーがクラス変数に存在するか確認
            if hasattr(self, key):
                # keyと一致するクラス変数の関数を呼び出す
                setattr(self, key, getattr(self.__class__, key).run(value))
            else:
                raise AttributeError(f"{key} is not a valid field")

    def save(self):
        pass

    def __str__(self):
        return self.title

    @abstractmethod
    def table_name(self):
        pass

    def migrate(self):
        # BaseFieldが継承されているかクラス変数を取得
        fields = [v for v in vars(self.__class__).values() if isinstance(v, BaseField)]
        for field in fields:
            print(field, "クラス名", field.__class__.__name__)
        print(self.table_name())


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
    def __init__(self, record_name, max_length=1000):
        super().__init__(record_name)
        self.max_length = max_length

    def run(self, value):
        if not isinstance(value, str):
            raise ValueError(f"{self.record_name} must be a string")
        if len(value) > self.max_length:
            raise ValueError(f"Length of {self.record_name} is too long")
        return value


class IntegerField(BaseField):
    def __init__(self, record_name):
        super().__init__(record_name)

    def run(self, value):
        if not isinstance(value, int):
            raise ValueError(f"{self.record_name} must be a integer")
        return value


if __name__ == "__main__":

    class TestModel(Model):
        title = CharField("title")
        content = CharField("content")
        number = IntegerField("number")

        def table_name(self):
            return "test_model"

    test = TestModel(title="test", content="test")
    # print(test.title)
    # print(test.content)
    test.migrate()
