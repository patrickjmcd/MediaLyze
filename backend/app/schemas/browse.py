from pydantic import BaseModel


class BrowseEntry(BaseModel):
    name: str
    path: str
    is_dir: bool


class BrowseResponse(BaseModel):
    current_path: str
    parent_path: str | None
    entries: list[BrowseEntry]

