import os
import sys

module_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(module_path)

from notion_api.orm import models
from notion_api.services.v1.databases import DataBaseService
from notion_api.domains.databases_domain import DatabaseTitle
from notion_api.domains.databases_domain import Title


class TestModel(models.Model):
    username = models.CharField("Username", max_length=1000, is_required=True)
    number = models.IntegerField("Number", is_required=True)
    selects = models.SelectField(
        "Selects",
        [
            models.SelectField.option("a"),
            models.SelectField.option("b"),
            models.SelectField.option("c"),
        ],
        is_required=True,
    )
    multi_selects = models.MultiSelectField(
        "MultiSelects",
        [
            models.MultiSelectField.option("x"),
            models.MultiSelectField.option("y"),
            models.MultiSelectField.option("z"),
        ],
        is_required=False,
    )
    date_field = models.DateField("DateField", is_required=False)
    bool_field = models.BoolField("BoolField", is_required=False)

    @classmethod
    def table_name(cls):
        return "create_table"


def test_db_migrate():
    TestModel.migrate(parent_id="a214e6c2d6e044d39cb5b98dc438c5dc")
    assert True


def test_db_migrate_and_create():
    model = TestModel.migrate(parent_id="a214e6c2d6e044d39cb5b98dc438c5dc")
    database_id = model["database_id"]

    create_record = TestModel(
        username="test",
        number=1,
        selects="a",
        multi_selects=["x", "y"],
        date_field="2021-01-01",
        bool_field=True,
    )
    create_record.save(database_id)

    assert True
