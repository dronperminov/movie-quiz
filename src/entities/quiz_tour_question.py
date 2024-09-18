from dataclasses import dataclass

from src.entities.question import Question


@dataclass
class QuizTourQuestion:
    question_id: int
    question: Question
    answer_time: float

    def to_dict(self) -> dict:
        return {
            "question_id": self.question_id,
            "question": self.question.to_dict(),
            "answer_time": self.answer_time
        }

    @classmethod
    def from_dict(cls: "QuizTourQuestion", data: dict) -> "QuizTourQuestion":
        return cls(
            question_id=data["question_id"],
            question=Question.from_dict(data["question"]),
            answer_time=data["answer_time"]
        )
