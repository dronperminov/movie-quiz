import json
import re
from dataclasses import dataclass, field
from typing import Dict, Optional

from fastapi import Query

from src.enums import QuizTourType
from src.utils.queries import enum_query


@dataclass
class QuizToursSearch:
    query: str = ""
    completed_type: str = ""
    quiz_tour_types: Dict[QuizTourType, bool] = field(default_factory=dict)
    tags: Dict[str, bool] = field(default_factory=dict)

    page: int = 0
    page_size: int = 10

    def to_query(self) -> dict:
        return {
            **self.to_name_query(),
            **enum_query("quiz_tour_type", self.quiz_tour_types),
            **enum_query("tags", self.tags),
        }

    def to_name_query(self) -> dict:
        return {"name": {"$regex": re.escape(self.query), "$options": "i"}} if self.query else {}

    def check_complete(self, answers: int, total: int) -> bool:
        if self.completed_type == "completed":
            return answers == total

        if self.completed_type == "started":
            return 0 < answers < total

        if self.completed_type == "unstarted":
            return answers == 0

        return True


@dataclass
class QuizToursSearchQuery:
    query: Optional[str] = Query(None)
    completed_type: Optional[str] = Query(None)
    quiz_tour_types: Optional[str] = Query(None)
    tags: Optional[str] = Query(None)

    def is_empty(self) -> bool:
        return self.query is None and self.completed_type is None and self.quiz_tour_types is None and self.tags is None

    def to_params(self, with_user: bool) -> Optional[QuizToursSearch]:
        if self.is_empty():
            return None

        return QuizToursSearch(
            query=self.query if self.query is not None else "",
            completed_type=self.completed_type if self.completed_type is not None and with_user else "all",
            quiz_tour_types=json.loads(self.quiz_tour_types) if self.quiz_tour_types is not None else {},
            tags=json.loads(self.tags) if self.tags is not None else {}
        )
