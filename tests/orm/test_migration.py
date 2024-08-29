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


def test_model_filter():
    # First, migrate the TestModel to create the database
    migration_result = TestModel.migrate(parent_id="a214e6c2d6e044d39cb5b98dc438c5dc")
    database_id = migration_result["database_id"]

    # Create some test records
    test_records = [
        TestModel(
            username="user1",
            number=10,
            selects="a",
            multi_selects=["x", "y"],
            date_field="2021-01-01",
            bool_field=True,
        ),
        TestModel(
            username="user2",
            number=20,
            selects="b",
            multi_selects=["y", "z"],
            date_field="2021-02-01",
            bool_field=False,
        ),
        TestModel(
            username="user3",
            number=30,
            selects="c",
            multi_selects=["x", "z"],
            date_field="2021-03-01",
            bool_field=True,
        ),
    ]

    # Save the test records
    for record in test_records:
        record.save(database_id)

    # Test filtering by username (contains)
    filtered_records = TestModel.filter(database_id, username={"contains": "user"})
    assert len(filtered_records) == 3

    for record in filtered_records:
        assert "user" in record.username
    # Test filtering by 2 conditions
    filtered_records = TestModel.filter(
        database_id, number={"greater_than": 10}, selects={"equals": "c"}
    )
    for record in filtered_records:
        assert record.number > 10
        assert record.selects == "c"
