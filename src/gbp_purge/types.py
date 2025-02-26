from typing import Protocol


class BuildLike(Protocol):
    machine: str
    build_id: str
