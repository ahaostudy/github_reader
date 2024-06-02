from typing import Optional
from typing import TypedDict
from dataclasses import dataclass


@dataclass
class Input:
    owner: str
    path: str
    recursion: bool
    repo: str


class Output(TypedDict, total=False):
    children: Optional[str]
    status: bool
    status_msg: str
    message: str
