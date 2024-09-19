from dataclasses import dataclass
from typing import List

from src.entities.analytics_entities.answer_time_analytics import AnswerTimeAnalytics
from src.entities.analytics_entities.questions_count_analytics import QuestionsCountAnalytics


@dataclass
class MainAnalytics:
    questions: QuestionsCountAnalytics
    time: AnswerTimeAnalytics

    @classmethod
    def evaluate(cls: "MainAnalytics", questions: List[dict]) -> "MainAnalytics":
        return cls(
            questions=QuestionsCountAnalytics.evaluate(questions),
            time=AnswerTimeAnalytics.evaluate(questions)
        )
