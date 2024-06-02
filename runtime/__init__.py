from typing import Generic, TypeVar

T = TypeVar('T')


class Args(Generic[T]):
    def __init__(self, ipt: T):
        self.input = ipt
