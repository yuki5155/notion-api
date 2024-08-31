# Notion API ORM

This Python library provides an easy-to-use Object-Relational Mapping (ORM) interface for the Notion API. It simplifies database operations in Notion, allowing you to interact with your Notion databases using Python objects.

## Features

- Create, read, update, and delete Notion database records
- Define database schemas using Python classes
- Automatic migration of database schemas to Notion
- Filtering and querying of database records
- Support for various field types: CharField, IntegerField, SelectField, MultiSelectField, DateField, BoolField

## Installation

You can install this library directly from the GitHub repository:

```bash
pip install git+https://github.com/yuki5155/notion-api.git
```

## Quick Start

### 1. Define your model

```python
from notion_api.orm import models

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
        return "MyTestTable"
```

### 2. Migrate the model to Notion

```python
migration_result = TestModel.migrate(parent_id="your_notion_page_id")
database_id = migration_result["database_id"]
```

### 3. Create a new record

```python
new_record = TestModel(
    username="john_doe",
    number=42,
    selects="a",
    multi_selects=["x", "y"],
    date_field="2023-05-01",
    bool_field=True
)
new_record.save(database_id)
```

### 4. Query records

```python
# Filter records
filtered_records = TestModel.filter(
    database_id,
    username={"contains": "john"},
    number={"greater_than": 40}
)

# Filter with OR condition
or_filtered_records = TestModel.filter(
    database_id,
    _operator="or",
    number={"greater_than": 50},
    selects={"equals": "a"}
)
```

### 5. Update a record

```python
record_to_update = filtered_records[0]
record_to_update.number = 99
record_to_update.update(database_id)
```

### 6. Delete a record

```python
record_to_delete = filtered_records[0]
record_to_delete.delete()
```

## Advanced Usage

### Custom Filtering

You can use various filtering conditions for different field types:

- CharField: equals, does_not_equal, contains, does_not_contain, starts_with, ends_with
- IntegerField: equals, does_not_equal, greater_than, less_than, greater_than_or_equal_to, less_than_or_equal_to
- SelectField: equals, does_not_equal, is_empty, is_not_empty
- MultiSelectField: contains, does_not_contain, is_empty, is_not_empty
- DateField: equals, before, after, on_or_before, on_or_after, is_empty, is_not_empty
- BoolField: equals, does_not_equal

Example:
```python
complex_filter = TestModel.filter(
    database_id,
    username={"starts_with": "j"},
    number={"greater_than_or_equal_to": 10, "less_than": 50},
    date_field={"after": "2023-01-01", "before": "2023-12-31"}
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.