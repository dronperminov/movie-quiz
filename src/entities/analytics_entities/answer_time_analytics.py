from dataclasses import dataclass
from typing import Dict, List


@dataclass
class AnswerTimeAnalytics:
    total: float
    total_mean: float
    correct_mean: float
    incorrect_mean: float

    histogram: Dict[str, int]
    histogram_correct: Dict[str, int]
    histogram_incorrect: Dict[str, int]
    histogram_keys = ["0-2", "2-4", "4-7", "7-10", "10-15", "15-20", "20-30", "30-60", "60+"]

    @classmethod
    def evaluate(cls: "AnswerTimeAnalytics", questions: List[dict]) -> "AnswerTimeAnalytics":
        answer = {False: [], True: []}
        histogram = {key: 0 for key in AnswerTimeAnalytics.histogram_keys}
        histograms = {
            False: {key: 0 for key in AnswerTimeAnalytics.histogram_keys},
            True: {key: 0 for key in AnswerTimeAnalytics.histogram_keys}
        }

        for question in questions:
            if question["answer_time"] is None:
                continue

            answer[question["correct"]].append(question["answer_time"])
            histogram[AnswerTimeAnalytics.get_key(question["answer_time"])] += 1
            histograms[question["correct"]][AnswerTimeAnalytics.get_key(question["answer_time"])] += 1

        total_times = answer[False] + answer[True]

        total_mean = AnswerTimeAnalytics.mean(total_times)
        correct = AnswerTimeAnalytics.mean(answer[True])
        incorrect = AnswerTimeAnalytics.mean(answer[False])
        return AnswerTimeAnalytics(
            total=sum(total_times),
            total_mean=total_mean,
            correct_mean=correct,
            incorrect_mean=incorrect,

            histogram=histogram,
            histogram_correct=histograms[True],
            histogram_incorrect=histograms[False]
        )

    @staticmethod
    def mean(values: List[float]) -> float:
        return 0 if len(values) == 0 else sum(values) / len(values)

    @staticmethod
    def get_key(time: float) -> str:
        offsets = [2, 4, 7, 10, 15, 20, 30, 60]

        for i, offset in enumerate(offsets):
            if time < offset:
                return AnswerTimeAnalytics.histogram_keys[i]

        return AnswerTimeAnalytics.histogram_keys[-1]
