from enum import Enum


class QuizTourType(Enum):
    REGULAR = "regular"
    ALPHABET = "alphabet"
    STAIRS = "stairs"
    LETTER = "letter"
    N_LETTERS = "n_letters"
    MIRACLES_FIELD = "miracles_field"
    CHAIN = "chain"

    def to_rus(self) -> str:
        quiz_tour_type2rus = {
            QuizTourType.REGULAR: "классический",
            QuizTourType.ALPHABET: "алфавит",
            QuizTourType.STAIRS: "лесенка",
            QuizTourType.LETTER: "на одну букву",
            QuizTourType.N_LETTERS: "N букв",
            QuizTourType.MIRACLES_FIELD: "поле чудес",
            QuizTourType.CHAIN: "цепочка"
        }
        return quiz_tour_type2rus[self]
