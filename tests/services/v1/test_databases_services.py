import os
import sys

module_path = os.path.join(os.path.dirname(__file__), '..', '..', "..", "..")
sys.path.append(module_path)
from notion_api.services.v1.databases import DataBaseService

def test_get_databases_detail():

    d = DataBaseService()
    data = d.get_notion_databases("6ef167bccb674124810c99f06ea1da8f")
    
    assert data.title[0].plain_text == '財務諸表'
    assert data.parent["type"] == "page_id"
    assert data.parent["page_id"].replace("-", "") == "00f4b5a76828414b8f56ab0eb2a6c0ea"
    assert isinstance(data.get_all_properties(), list)
    assert data.properties['株価(3/1)'].name == "株価(3/1)"
    assert data.properties["決算"].type == "select"
    assert data.properties["決算"].select["options"][0]["name"] == "年次決算"

def test_create_database():
    d = DataBaseService()
    parent_id = "a214e6c2d6e044d39cb5b98dc438c5dc"
    database_property = {
        "Name": {"title": {}},
        "Tags": {"multi_select": {"options": [{"name": "tag1"}, {"name": "tag2"}]}}
    }
    response = d.create_notion_database("Grocery List", parent_id, database_property)
    assert response["code"] == 200
