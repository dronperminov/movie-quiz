from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class PeriodAnalyticsItem:
    label: str
    start_date: datetime
    end_date: datetime
    time: float
    correct: int
    incorrect: int
    total: int


@dataclass
class PeriodAnalytics:
    data: List[PeriodAnalyticsItem]
    group_by: str

    @classmethod
    def evaluate(cls: "PeriodAnalytics", questions: List[dict]) -> "PeriodAnalytics":
        if not questions:
            return cls(data=[], group_by="")

        questions = sorted(questions, key=lambda question: question["timestamp"])
        min_date, max_date = questions[0]["timestamp"], questions[-1]["timestamp"]
        delta = (max_date - min_date).days

        if delta < 3:
            group_by = "hour"
        elif delta <= 30:
            group_by = "day"
        elif delta < 200:
            group_by = "week"
        else:
            group_by = "month"

        groups = [[questions[0]]]

        for question in questions[1:]:
            if PeriodAnalytics.__is_new_date(groups[-1][-1]["timestamp"], question["timestamp"], group_by=group_by):
                groups.append([question])
            else:
                groups[-1].append(question)

        return cls(data=[PeriodAnalytics.__evaluate_group(group, group_by) for group in groups], group_by=group_by)

    @staticmethod
    def __is_new_date(prev_date: datetime, new_date: datetime, group_by: str) -> bool:
        if group_by == "hour":
            return (prev_date.year, prev_date.month, prev_date.day, prev_date.hour) != (new_date.year, new_date.month, new_date.day, new_date.hour)

        if group_by == "day":
            return new_date.date() != prev_date.date()

        if group_by == "week":
            return new_date.isocalendar().week != prev_date.isocalendar().week

        if group_by == "month":
            return (prev_date.year, prev_date.month) != (new_date.year, new_date.month)

        raise ValueError(f'Invalid group by "{group_by}"')

    @staticmethod
    def __evaluate_group(questions: List[dict], group_by: str) -> PeriodAnalyticsItem:
        if group_by == "hour":
            label = questions[0]["timestamp"].strftime("%H:00\\n%d.%m")
        elif group_by == "day":
            label = questions[0]["timestamp"].strftime("%d.%m\\n%Y")
        elif group_by == "week":
            label = f'{questions[0]["timestamp"].strftime("%d.%m.%Y")}\\n{questions[-1]["timestamp"].strftime("%d.%m.%Y")}'
        else:
            months = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]
            label = f'{months[questions[0]["timestamp"].month]}\\n{questions[0]["timestamp"].year}'

        times = []
        answers = {True: 0, False: 0}

        for question in questions:
            times.append(question["answer_time"])
            answers[question["correct"]] += 1

        return PeriodAnalyticsItem(
            label=label,
            start_date=questions[0]["timestamp"],
            end_date=questions[-1]["timestamp"],
            time=sum(times) / len(times),
            correct=answers[True],
            incorrect=answers[False],
            total=len(questions)
        )
