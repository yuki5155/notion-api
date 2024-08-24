from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class User:
    object: str
    id: str


@dataclass
class TextContent:
    content: str
    link: Optional[str]


@dataclass
class Annotations:
    bold: bool
    italic: bool
    strikethrough: bool
    underline: bool
    code: bool
    color: str


@dataclass
class Title:
    type: str
    text: TextContent
    annotations: Annotations
    plain_text: str
    href: Optional[str] = None


@dataclass
class SelectOption:
    id: str
    name: str
    color: str
    description: Optional[str] = None


class Property:
    def __init__(self, id, type, **kwargs):
        self.id = id
        self.type = type
        self.name = kwargs.get("name")
        self.title = kwargs.get("title")
        self.rich_text = kwargs.get("rich_text")
        self.number = kwargs.get("number")
        self.select = kwargs.get("select")
        self.multi_select = kwargs.get("multi_select")
        self.date = kwargs.get("date")
        self.people = kwargs.get("people")
        self.files = kwargs.get("files")
        self.checkbox = kwargs.get("checkbox")
        self.url = kwargs.get("url")
        self.email = kwargs.get("email")
        self.phone_number = kwargs.get("phone_number")
        self.formula = kwargs.get("formula")
        self.relation = kwargs.get("relation")
        self.rollup = kwargs.get("rollup")
        self.created_time = kwargs.get("created_time")
        self.created_by = kwargs.get("created_by")
        self.last_edited_time = kwargs.get("last_edited_time")
        self.last_edited_by = kwargs.get("last_edited_by")


@dataclass
class Database:
    object: str
    id: str
    cover: Optional[Any]
    icon: Optional[Any]
    created_time: str
    created_by: User
    last_edited_by: User
    last_edited_time: str
    title: List[Title]
    description: List[Any]
    is_inline: bool
    properties: Dict[str, Property]
    parent: Dict[str, Any]
    url: str
    public_url: Optional[str]
    archived: bool
    in_trash: bool
    request_id: str

    def get_all_properties(self):
        return list(self.properties.keys())


# 辞書データをクラスインスタンスに変換する関数
def NewDatabase(data: Dict[str, Any]) -> Database:
    data = data["body"]
    return Database(
        object=data["object"],
        id=data["id"],
        cover=data["cover"],
        icon=data["icon"],
        created_time=data["created_time"],
        created_by=User(**data["created_by"]),
        last_edited_by=User(**data["last_edited_by"]),
        last_edited_time=data["last_edited_time"],
        title=[
            Title(
                type=title["type"],
                text=TextContent(**title["text"]),
                annotations=Annotations(**title["annotations"]),
                plain_text=title["plain_text"],
                href=title["href"],
            )
            for title in data["title"]
        ],
        description=data["description"],
        is_inline=data["is_inline"],
        properties={k: Property(**v) for k, v in data["properties"].items()},
        parent=data["parent"],
        url=data["url"],
        public_url=data["public_url"],
        archived=data["archived"],
        in_trash=data["in_trash"],
        request_id=data["request_id"],
    )


# ----------------------------------------------------------------
# create parameters
# ----------------------------------------------------------------


@dataclass
class Text:
    content: str

    def to_dict(self):
        return {"content": self.content}


@dataclass
class RichText:
    type: str = "text"
    text: Text = field(default_factory=Text)

    def to_dict(self):
        return {"type": self.type, "text": self.text.to_dict()}


@dataclass
class MultiSelectOption:
    name: str
    color: str = "default"

    def to_dict(self):
        return {"name": self.name, "color": self.color}


@dataclass
class MultiSelect:
    options: List[MultiSelectOption] = field(default_factory=list)

    def to_dict(self):
        return {
            "multi_select": {"options": [option.to_dict() for option in self.options]}
        }


@dataclass
class Parent:
    type: str = "page_id"
    page_id: str = ""

    def to_dict(self):
        return {"type": self.type, "page_id": self.page_id}


@dataclass
class CreateDatabaseParams:
    parent: Parent
    title: List[RichText]
    properties: dict

    def to_dict(self):
        return {
            "parent": self.parent.to_dict(),
            "title": self.title.to_dict(),
            "properties": self.properties.to_dict(),
        }


@dataclass
class DatabaseTitle:
    content: str
    link: Optional[str] = None

    def to_dict(self):
        return {"content": self.content, "link": self.link}


@dataclass
class FilteredDatabaseRecord:
    id: str
    properties: Dict[str, Any]
    created_time: datetime
    last_edited_time: datetime

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FilteredDatabaseRecord":
        return cls(
            id=data["id"],
            properties=data["properties"],
            created_time=datetime.fromisoformat(data["created_time"].rstrip("Z")),
            last_edited_time=datetime.fromisoformat(
                data["last_edited_time"].rstrip("Z")
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "properties": self.properties,
            "created_time": self.created_time.isoformat() + "Z",
            "last_edited_time": self.last_edited_time.isoformat() + "Z",
        }


if __name__ == "__main__":
    p = Parent(page_id="sample")
