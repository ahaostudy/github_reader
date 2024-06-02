from typing import TypedDict
from dataclasses import dataclass
from typing import Optional


@dataclass
class Input:
    owner: str
    paths: list[str]
    repo: str


class FilesItems(TypedDict, total=False):
    content: str
    path: str


class Output(TypedDict, total=False):
    files: Optional[list[FilesItems]]
    status: bool
    status_msg: str
    message: str
