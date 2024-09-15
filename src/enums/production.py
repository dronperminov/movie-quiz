from enum import Enum
from typing import List


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

    @classmethod
    def from_countries(cls: "Production", countries: List[str]) -> "List[Production]":
        country2production = {
            "Россия": Production.RUSSIAN,
            "СССР": Production.RUSSIAN,
            "Корея Южная": Production.KOREAN,
            "Турция": Production.TURKISH
        }

        return list({country2production.get(country, Production.FOREIGN) for country in countries})
