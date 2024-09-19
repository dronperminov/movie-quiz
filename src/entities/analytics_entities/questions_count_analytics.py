from dataclasses import dataclass
from typing import List


@dataclass
class QuestionsCountAnalytics:
    total: int
    correct: int
    incorrect: int

    def __post_init__(self) -> None:
        self.correct_percents = self.correct / max(self.total, 1) * 100
        self.incorrect_percents = self.incorrect / max(self.total, 1) * 100

    @classmethod
    def evaluate(cls: "QuestionsCountAnalytics", questions: List[dict]) -> "QuestionsCountAnalytics":
        answer = {False: 0, True: 0}

        for question in questions:
            answer[question["correct"]] += 1

        return QuestionsCountAnalytics(total=len(questions), correct=answer[True], incorrect=answer[False])
