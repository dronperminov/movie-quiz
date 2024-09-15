from enum import Enum


class Production(Enum):
    RUSSIAN = "russian"
    KOREAN = "korean"
    TURKISH = "turkish"
    FOREIGN = "foreign"

    def to_rus(self) -> str:
        production2rus = {
            Production.RUSSIAN: "российское",
            Production.KOREAN: "корейское",
            Production.TURKISH: "турецкое",
            Production.FOREIGN: "зарубежное"
        }

        return production2rus[self]
