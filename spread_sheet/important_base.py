import inspect


# クラスの定義
class MyClass:
    class_var = "I am a class variable"
    another_class_var = 123


class Hoge(MyClass):
    class_var = "I am a class variable"
    another_class_var = 123


def default_model_func():
    # Pythonの組み込みオブジェクトが持つ属性を取得
    base_attrs = set(dir(type("dummy", (object,), {})))

    # 自分で定義したクラスの属性を取得
    class_attrs = set(dir(MyClass))

    # 組み込み属性を除外
    my_class_vars = class_attrs - base_attrs

    # 結果を表示
    print(my_class_vars)


## abtract class
from abc import ABCMeta, abstractmethod


class BaseField(metaclass=ABCMeta):
    @abstractmethod
    def sample_method(self):
        pass

    def __str__(self) -> str:
        return self.__class__.__name__


class StringField:
    def __init__(
        self,
    ):
        # 変数名を取得
        frame = inspect.currentframe().f_back
        var_name = None
        for var in frame.f_globals:
            if frame.f_globals[var] is self:
                var_name = var
                break

        self.value = var_name

    def sample_method(self):
        print("StringField")


def default_model_func(ccc):
    # Pythonの組み込みオブジェクトが持つ属性を取得
    base_attrs = set(dir(type("dummy", (object,), {})))

    # 自分で定義したクラスの属性を取得
    class_attrs = set(dir(a))

    # 組み込み属性を除外
    my_class_vars = class_attrs - base_attrs

    # 結果を表示
    print(my_class_vars)


a = StringField()
print(a.value)
