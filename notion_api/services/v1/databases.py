import sys
import os
module_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.append(module_path)
from client import BaseAPIClient
from exceptions import APIClientNotFountError
from .v1_base_service import BaseService
from domains.databases_domain import (
    NewDatabase, CreateDatabaseParams, Parent, RichText, Text, MultiSelectOption
)

class DataBaseService(BaseService):
    def get_notion_databases(self, database_id):
        db = NewDatabase(self.client.get(f'v1/databases/{database_id}'))
        return db
    
    def create_notion_database(self, title: str, parent_id: str, properties: dict):
        database_title = [RichText(text=Text(content=title))]
        
        data = {
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": title,
                        "link": None
                    }
                }
            ],
            "parent": {
                "type": "page_id",
                "page_id": parent_id
            },
            "properties": properties
        }
        return self.client.post('v1/databases', data)