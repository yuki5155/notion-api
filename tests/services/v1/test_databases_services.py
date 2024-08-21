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
    database_id = "6ef167bccb674124810c99f06ea1da8f"

    for i in d.get_database_records(database_id):

        if i["株価(3/1)"]["number"] is not None:
            assert True


def test_filter_records():
    d = DataBaseService()
    database_id = "6ef167bccb674124810c99f06ea1da8f"
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
