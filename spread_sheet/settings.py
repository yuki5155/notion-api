import ast


class ClassVisitor(ast.NodeVisitor):
    def __init__(self, base_class):
        self.base_class = base_class
        self.derived_classes = []

    def visit_ClassDef(self, node):
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == self.base_class:
                self.derived_classes.append(node.name)
        # 再帰的に探索を続ける
        self.generic_visit(node)


def find_derived_classes(filename, base_class):
    with open(filename, "r") as source:
        tree = ast.parse(source.read())
    visitor = ClassVisitor(base_class)
    visitor.visit(tree)
    return visitor.derived_classes


if __name__ == "__main__":
    # BaseClassを継承したクラスを探索
    filename = "/workspaces/programming-searching-engine-datae/spread_sheet/important_base.py"  # 探索対象のPythonファイル名
    base_class = "MyClass"  # 探索対象のベースクラス名
    print(find_derived_classes(filename, base_class))
