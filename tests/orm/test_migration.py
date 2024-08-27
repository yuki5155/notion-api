import os
import sys

module_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(module_path)

from notion_api.domains.orm import models
from notion_api.services.v1.databases import DataBaseService
from notion_api.domains.databases_domain import DatabaseTitle
from notion_api.domains.databases_domain import Title


class TestModel(models.Model):
    username = models.CharField("Username", max_length=1000, is_required=True)

    def table_name():
        return "sample_table"


def test_db_migrate():
    TestModel.migrate(parent_id="a214e6c2d6e044d39cb5b98dc438c5dc")
    print("Test: Migrate without initialization")
    assert True
