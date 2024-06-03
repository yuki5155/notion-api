import sys
import os
module_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.append(module_path)
from client import BaseAPIClient
from exceptions import APIClientNotFountError
from .v1_base_service import BaseService
from domains.databases_domain import NewDatabase

class DataBaseService(BaseService):
    def get_notion_databases(self, database_id):
        db = NewDatabase(self.client.get(f'v1/databases/{database_id}'))
        return db