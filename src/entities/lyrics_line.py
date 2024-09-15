import re
from dataclasses import dataclass

from Levenshtein import ratio


@dataclass
class LyricsLine:
    time: float
    text: str

    def to_dict(self) -> dict:
        return {"time": self.time, "text": self.text}

    @classmethod
    def from_dict(cls: "LyricsLine", data: dict) -> "LyricsLine":
        return cls(time=data["time"], text=data["text"])

    @classmethod
    def from_lrc(cls: "LyricsLine", lrc_line: str) -> "LyricsLine":
        match = re.search(r"^\[(?P<minute>\d+):(?P<second>\d+\.\d+)] (?P<text>.*)$", lrc_line)
        text, minute, second = match.group("text").strip(), float(match.group("minute")), float(match.group("second"))
        return LyricsLine(time=round(minute * 60 + second, 2), text=text)

    def is_russian(self) -> bool:
        return len(re.findall(r"[а-яА-ЯёЁ]", self.text)) > len(re.findall(r"\w", self.text)) * 0.5

    def is_parenthesis(self) -> bool:
        return re.fullmatch(r"\([^)]+\)", self.text) is not None

    def preprocess(self) -> "LyricsLine":
        text = self.text.lower()
        text = re.sub(r"-", "", text)
        text = re.sub(r"\s*\([^)]+\)\s*", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return LyricsLine(time=self.time, text=text)

    def is_similar(self, line: "LyricsLine", threshold: float = 0.9) -> bool:
        words1 = re.findall(r"\w+", self.text)
        words2 = re.findall(r"\w+", line.text)
        return ratio(words1, words2) > threshold
