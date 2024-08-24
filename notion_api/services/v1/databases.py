import sys
import os

module_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(module_path)
from notion_api.utils.client import BaseAPIClient
from notion_api.utils.exceptions import APIClientNotFountError
from .v1_base_service import BaseService
from notion_api.domains.databases_domain import (
    NewDatabase,
    CreateDatabaseParams,
    Parent,
    RichText,
    Text,
    MultiSelectOption,
    DatabaseTitle,
)
from notion_api.utils.database_record_ops import DatabaseRecord


class DataBaseService(BaseService):
    def get_notion_databases(self, database_id):
        db = NewDatabase(self.client.get(f"v1/databases/{database_id}"))
        return db

    def create_notion_database(
        self, title: DatabaseTitle, parent_id: str, properties: dict
    ):
        if title is None:
            raise ValueError("Title is required")

        if parent_id is None:
            raise ValueError("Parent ID is required")
        if properties is None:
            raise ValueError("Properties is required")

        if not isinstance(title, DatabaseTitle):
            raise ValueError(
                f"Title must be an instance of DatabaseTitle, got {type(title)} instead"
            )

        data = {
            "title": [{"type": "text", "text": title.to_dict()}],
            "parent": {"type": "page_id", "page_id": parent_id},
            "properties": properties,
        }
        return self.client.post("v1/databases", data)

    def get_database_records(self, database_id: str):
        return [
            p["properties"]
            for p in self.client.post(f"v1/databases/{database_id}/query")["body"][
                "results"
            ]
        ]

    def filter_database_records(self, database_id: str, filter_params: dict):
        if not isinstance(filter_params, dict):
            raise ValueError(
                f"Filter params must be a dictionary, got {type(filter_params)} instead"
            )
        return [
            p["properties"]
            for p in self.client.post(
                f"v1/databases/{database_id}/query", filter_params
            )["body"]["results"]
        ]

    def insert_record(self, database_id: str, record_data: dict):
        """
        データベースに新しいレコードを挿入します。

        :param database_id: 挿入先のデータベースID
        :param record_data: 挿入するレコードのデータ
        :return: 作成されたレコードの情報
        """
        if not database_id:
            raise ValueError("Database ID is required")
        if not record_data:
            raise ValueError("Record data is required")

        # Ensure the correct structure of the record_data
        if "parent" not in record_data or "properties" not in record_data:
            raise ValueError("Invalid record data structure")

        response = self.client.post("v1/pages", record_data)

        if response["code"] == 200:
            return response["body"]
        else:
            raise APIClientNotFountError(f"Failed to insert record: {response}")

    def update_record(self, page_id: str, record: DatabaseRecord):
        """
        データベース内の既存のレコードを更新します。

        :param page_id: 更新するレコード（ページ）のID
        :param record: 更新するレコードの情報（DatabaseRecordオブジェクト）
        :return: 更新されたレコードの情報
        """
        if not page_id:
            raise ValueError("Page ID is required")
        if not isinstance(record, DatabaseRecord):
            raise ValueError("record must be an instance of DatabaseRecord")

        data = record.to_dict()
        # parentプロパティは更新時に不要なので削除
        data.pop("parent", None)

        response = self.client.patch(f"v1/pages/{page_id}", data)

        if response["code"] == 200:
            return response["body"]
        else:
            raise APIClientNotFountError(f"Failed to update record: {response}")
