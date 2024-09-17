from dataclasses import dataclass
from typing import Optional


@dataclass
class QuestionAnswer:
    correct: bool
    answer_time: Optional[float]

    @classmethod
    def from_dict(cls: "QuestionAnswer", data: dict) -> "QuestionAnswer":
        return cls(correct=data["correct"], answer_time=data["answer_time"])

    def to_dict(self) -> dict:
        return {"correct": self.correct, "answer_time": self.answer_time}
