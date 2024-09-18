from dataclasses import dataclass
from datetime import datetime
from typing import List, Set

from src.enums import QuizTourType


@dataclass
class QuizTour:
    quiz_tour_id: int
    quiz_tour_type: QuizTourType
    name: str
    description: str
    question_ids: List[int]
    image_url: str
    created_at: datetime
    created_by: str
    tags: List[str]

    def to_dict(self) -> dict:
        return {
            "quiz_tour_id": self.quiz_tour_id,
            "quiz_tour_type": self.quiz_tour_type.value,
            "name": self.name,
            "description": self.description,
            "question_ids": self.question_ids,
            "image_url": self.image_url,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls: "QuizTour", data: dict) -> "QuizTour":
        return cls(
            quiz_tour_id=data["quiz_tour_id"],
            quiz_tour_type=QuizTourType(data["quiz_tour_type"]),
            name=data["name"],
            description=data["description"],
            question_ids=data["question_ids"],
            image_url=data["image_url"],
            created_at=data["created_at"],
            created_by=data["created_by"],
            tags=data["tags"]
        )

    def remove_questions(self, question_ids: Set[int]) -> None:
        self.question_ids = [question_id for question_id in self.question_ids if question_id not in question_ids]

    def is_empty(self) -> bool:
        return len(self.question_ids) == 0
