import os
import sys

module_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(module_path)

from notion_api.orm import models
from notion_api.services.v1.databases import DataBaseService
from notion_api.domains.databases_domain import DatabaseTitle
from notion_api.domains.databases_domain import Title
import time


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


def test_model_filter_or():
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

    # Test OR filtering
    filtered_records = TestModel.filter(
        database_id,
        _operator="or",
        number={"greater_than": 25},
        selects={"equals": "a"},
    )

    assert len(filtered_records) == 2

    for record in filtered_records:
        assert record.number > 25 or record.selects == "a"

    # Additional check to ensure OR condition is working
    number_condition_met = any(record.number > 25 for record in filtered_records)
    select_condition_met = any(record.selects == "a" for record in filtered_records)

    assert (
        number_condition_met and select_condition_met
    ), "OR condition is not working as expected"


def test_model_update():
    # First, migrate the TestModel to create the database
    migration_result = TestModel.migrate(parent_id="a214e6c2d6e044d39cb5b98dc438c5dc")
    database_id = migration_result["database_id"]

    # Create a test record with a unique username
    unique_username = f"user_{int(time.time())}"  # Use timestamp to ensure uniqueness
    test_record = TestModel(
        username=unique_username,
        number=10,
        selects="a",
        multi_selects=["x", "y"],
        date_field="2021-01-01",
        bool_field=True,
    )
    test_record.save(database_id)

    # Find the record using the unique username
    filtered_records = TestModel.filter(
        database_id, username={"equals": unique_username}
    )
    assert len(filtered_records) == 1, "Expected to find exactly one record"

    original_record = filtered_records[0]

    # Update the record
    updated_record = TestModel(
        username=unique_username,  # Keep the username the same to find it again
        number=20,
        selects="b",
        multi_selects=["y", "z"],
        date_field="2021-02-01",
        bool_field=False,
    )

    page_id = original_record.get_page_id()
    updated_record.update(database_id, page_id)

    # Fetch the updated record
    filtered_records = TestModel.filter(
        database_id, username={"equals": unique_username}
    )
    assert len(filtered_records) == 1, "Expected to find exactly one record"

    fetched_record = filtered_records[0]

    # Assert that the record was updated correctly
    assert fetched_record.username == unique_username
    assert fetched_record.number == 20
    assert fetched_record.selects == "b"
    assert fetched_record.multi_selects == ["y", "z"]
    assert fetched_record.date_field == "2021-02-01"
    assert fetched_record.bool_field == False


def test_model_delete():
    # First, migrate the TestModel to create the database
    migration_result = TestModel.migrate(parent_id="a214e6c2d6e044d39cb5b98dc438c5dc")
    database_id = migration_result["database_id"]

    # Create a test record with a unique username
    unique_username = f"delete_test_user_{int(time.time())}"
    test_record = TestModel(
        username=unique_username,
        number=100,
        selects="a",
        multi_selects=["x", "y"],
        date_field="2021-01-01",
        bool_field=True,
    )
    test_record.save(database_id)

    # Find the record using the unique username
    filtered_records = TestModel.filter(
        database_id, username={"equals": unique_username}
    )
    assert len(filtered_records) == 1, "Expected to find exactly one record"

    record_to_delete = filtered_records[0]

    # Delete the record
    delete_result = record_to_delete.delete()
    assert delete_result, "Expected deletion to be successful"

    # Try to find the deleted record
    filtered_records_after_delete = TestModel.filter(
        database_id, username={"equals": unique_username}
    )
    assert (
        len(filtered_records_after_delete) == 0
    ), "Expected to find no records after deletion"


def test_model_delete_by_id():
    # First, migrate the TestModel to create the database
    migration_result = TestModel.migrate(parent_id="a214e6c2d6e044d39cb5b98dc438c5dc")
    database_id = migration_result["database_id"]

    # Create a test record with a unique username
    unique_username = f"delete_by_id_test_user_{int(time.time())}"
    test_record = TestModel(
        username=unique_username,
        number=200,
        selects="b",
        multi_selects=["y", "z"],
        date_field="2021-02-01",
        bool_field=False,
    )
    test_record.save(database_id)

    # Find the record using the unique username
    filtered_records = TestModel.filter(
        database_id, username={"equals": unique_username}
    )
    assert len(filtered_records) == 1, "Expected to find exactly one record"

    record_to_delete = filtered_records[0]
    page_id = record_to_delete.get_page_id()

    # Delete the record using delete_by_id
    delete_result = TestModel.delete_by_id(database_id, page_id)
    assert delete_result, "Expected deletion to be successful"

    # Try to find the deleted record
    filtered_records_after_delete = TestModel.filter(
        database_id, username={"equals": unique_username}
    )
    assert (
        len(filtered_records_after_delete) == 0
    ), "Expected to find no records after deletion"
