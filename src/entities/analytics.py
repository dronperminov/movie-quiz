from dataclasses import dataclass
from typing import List

from src.entities.analytics_entities.main_analytics import MainAnalytics
from src.entities.analytics_entities.period_analytics import PeriodAnalytics


@dataclass
class Analytics:
    main: MainAnalytics
    period: PeriodAnalytics

    @classmethod
    def evaluate(cls: "Analytics", questions: List[dict]) -> "Analytics":
        return cls(
            main=MainAnalytics.evaluate(questions),
            period=PeriodAnalytics.evaluate(questions)
        )
