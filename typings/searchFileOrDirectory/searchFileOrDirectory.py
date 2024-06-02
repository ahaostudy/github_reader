from dataclasses import dataclass
from typing import TypedDict


@dataclass
class Input:
    name: str
    owner: str
    repo: str


class ResultItems(TypedDict, total=False):
    path: str
    type: str


class Output(TypedDict, total=False):
    result: list[ResultItems]
    status: bool
    status_msg: str
    message: str
