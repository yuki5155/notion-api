import os
import sys

module_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
sys.path.append(module_path)
from notion_api.services.v1.databases import DataBaseService
from notion_api.domains.databases_domain import DatabaseTitle
from notion_api.utils.databases_filter_builders import (
    NumberFilterBuilder,
    FilterComposer,
)
from notion_api.services.v1.databases import DataBaseService
from notion_api.utils.exceptions import APIClientNotFountError
from notion_api.utils.database_record_ops import DatabaseRecord

database_id = "6ef167bccb674124810c99f06ea1da8f"


def test_get_databases_detail():

    d = DataBaseService()
    data = d.get_notion_databases("6ef167bccb674124810c99f06ea1da8f")

    assert data.title[0].plain_text == "財務諸表"
    assert data.parent["type"] == "page_id"
    assert data.parent["page_id"].replace("-", "") == "00f4b5a76828414b8f56ab0eb2a6c0ea"
    assert isinstance(data.get_all_properties(), list)
    assert data.properties["株価(3/1)"].name == "株価(3/1)"
    assert data.properties["決算"].type == "select"
    assert data.properties["決算"].select["options"][0]["name"] == "年次決算"


# def test_create_database():
#     d = DataBaseService()
#     parent_id = "a214e6c2d6e044d39cb5b98dc438c5dc"
#     database_property = {
#         "Name": {"title": {}},
#         "Tags": {"multi_select": {"options": [{"name": "tag1"}, {"name": "tag2"}]}}
#     }
#     database_title = DatabaseTitle(content="Grocery List")
#     response = d.create_notion_database(database_title, parent_id, database_property)
#     assert response["code"] == 200


def test_get_all_records():
    d = DataBaseService()

    for i in d.get_database_records(database_id):

        if i["株価(3/1)"]["number"] is not None:
            assert True


def test_filter_records():
    d = DataBaseService()

    stock_price_threshold = 5000

    # NumberFilterBuilder を使用してフィルターを作成
    stock_price_filter = (
        NumberFilterBuilder("株価(3/1)").greater_than(stock_price_threshold).build()
    )

    # FilterComposer を使用してフィルターパラメータを構築
    filter_composer = FilterComposer()
    filter_params = filter_composer.add_filter(stock_price_filter).build()

    filtered_records = d.filter_database_records(database_id, filter_params)

    for record in filtered_records:
        assert record["株価(3/1)"]["number"] > stock_price_threshold

    # 少なくとも1つのレコードがフィルタリングされたことを確認
    filtered_records_list = list(filtered_records)
    assert len(filtered_records_list) > 0


# 複数条件のテストケース
def test_filter_records_multiple_conditions():
    d = DataBaseService()
    database_id = "6ef167bccb674124810c99f06ea1da8f"
    stock_price = 1000
    roe = 12

    stock_price_filter = (
        NumberFilterBuilder("株価(3/1)").greater_than(stock_price).build()
    )
    roe_filter = NumberFilterBuilder("ROE").greater_than(roe).build()

    filter_composer = FilterComposer()
    filter_params = (
        filter_composer.add_filter(stock_price_filter).add_filter(roe_filter).build()
    )

    filtered_records = d.filter_database_records(database_id, filter_params)

    for record in filtered_records:
        print(record)
        assert record["株価(3/1)"]["number"] > stock_price
        assert record["ROE"]["number"] > roe

    # 少なくとも1つのレコードがフィルタリングされたことを確認
    filtered_records_list = list(filtered_records)
    assert len(filtered_records_list) > 0


def test_filter_records_or_condition():
    d = DataBaseService()
    database_id = "6ef167bccb674124810c99f06ea1da8f"
    stock_price_threshold = 10000
    roe_threshold = 20

    # Create filters
    stock_price_filter = (
        NumberFilterBuilder("株価(3/1)").greater_than(stock_price_threshold).build()
    )
    roe_filter = NumberFilterBuilder("ROE").greater_than(roe_threshold).build()

    # Use FilterComposer to build OR filter
    filter_composer = FilterComposer()
    filter_params = (
        filter_composer.add_filter(stock_price_filter)
        .add_filter(roe_filter)
        .build("or")
    )

    filtered_records = d.filter_database_records(database_id, filter_params)

    for record in filtered_records:
        assert (
            record["株価(3/1)"]["number"] > stock_price_threshold
            or record["ROE"]["number"] > roe_threshold
        )

    # Ensure at least one record was filtered
    filtered_records_list = list(filtered_records)
    assert len(filtered_records_list) > 0

    # Additional check to ensure OR condition is working
    only_high_stock_price = any(
        record["株価(3/1)"]["number"] > stock_price_threshold
        and record["ROE"]["number"] <= roe_threshold
        for record in filtered_records_list
    )
    only_high_roe = any(
        record["ROE"]["number"] > roe_threshold
        and record["株価(3/1)"]["number"] <= stock_price_threshold
        for record in filtered_records_list
    )

    assert (
        only_high_stock_price or only_high_roe
    ), "OR condition is not working as expected"


def test_insert_record():
    d = DataBaseService()

    record = DatabaseRecord(database_id)
    record.add_property("株価(3/1)", 9999)
    record.add_property("ROE", 20)
    record.add_property("決算", "年次決算")
    # record.add_property("テスト用", True)

    # Insert record
    new_record = d.insert_record(database_id, record.to_dict())

    # Verify the inserted record
    assert isinstance(new_record, dict)

    # Check the properties in the returned data
    result = new_record["properties"]
    assert result["株価(3/1)"]["number"] == 9999
    assert result["ROE"]["number"] == 20
    assert result["決算"]["select"]["name"] == "年次決算"


def test_update_record():
    d = DataBaseService()
    database_id = "6ef167bccb674124810c99f06ea1da8f"  # Test database ID

    # First, insert a new record
    insert_record = DatabaseRecord(database_id)
    insert_record.add_property("株価(3/1)", 1000)
    insert_record.add_property("ROE", 10)
    insert_record.add_property("決算", "年次決算")
    # insert_record.add_property("テスト用", True)

    new_record = d.insert_record(database_id, insert_record.to_dict())
    page_id = new_record["id"]

    # Now, update the record
    update_record = DatabaseRecord(database_id)
    update_record.add_property("株価(3/1)", 1500)
    update_record.add_property("ROE", 15)

    updated_record = d.update_record(page_id, update_record)

    # Verify the updated record
    assert isinstance(updated_record, dict)

    # Check the updated properties
    result = updated_record["properties"]
    assert result["株価(3/1)"]["number"] == 1500
    assert result["ROE"]["number"] == 15
    assert (
        result["決算"]["select"]["name"] == "年次決算"
    )  # This should remain unchanged
