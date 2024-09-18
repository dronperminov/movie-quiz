from dataclasses import dataclass
from typing import Dict

from src.utils.queries import enum_query


@dataclass
class TopPlayersQuery:
    tags: Dict[str, bool]

    def to_query(self) -> dict:
        return enum_query("tags", self.tags)
