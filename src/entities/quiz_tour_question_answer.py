from dataclasses import dataclass


@dataclass
class QuizTourQuestionAnswer:
    question_id: int
    correct: bool
    answer_time: float
