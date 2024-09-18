from dataclasses import dataclass
from datetime import datetime


@dataclass
class QuizTourAnswer:
    question_id: int
    username: str
    correct: bool
    timestamp: datetime
    answer_time: float

    def __post_init__(self) -> None:
        self.timestamp.replace(microsecond=0)

    def to_dict(self) -> dict:
        return {
            "question_id": self.question_id,
            "username": self.username,
            "correct": self.correct,
            "timestamp": self.timestamp,
            "answer_time": self.answer_time
        }

    @classmethod
    def from_dict(cls: "QuizTourAnswer", data: dict) -> "QuizTourAnswer":
        return cls(
            question_id=data["question_id"],
            username=data["username"],
            correct=data["correct"],
            timestamp=data["timestamp"],
            answer_time=data["answer_time"]
        )
