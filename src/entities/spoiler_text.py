from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class SpoilerText:
    text: str
    spoilers: List[Tuple[int, int]]

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "spoilers": [{"start": start, "end": end} for start, end in self.spoilers]
        }

    @classmethod
    def from_dict(cls: "SpoilerText", data: dict) -> "SpoilerText":
        return cls(
            text=data["text"],
            spoilers=[(span["start"], span["end"]) for span in data["spoilers"]]
        )
