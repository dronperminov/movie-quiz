from dataclasses import dataclass
from typing import List


@dataclass
class HistoryQuery:
    actions: List[str]
    limit: int = 100
    skip: int = 0
