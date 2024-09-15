from dataclasses import dataclass
from typing import List

from src.entities.lyrics_line import LyricsLine


@dataclass
class Lyrics:
    lines: List[LyricsLine]
    lrc: bool

    @classmethod
    def from_lrc(cls: "Lyrics", lyrics_str: str) -> "Lyrics":
        lines = []

        for line in lyrics_str.split("\n"):
            if (lyrics_line := LyricsLine.from_lrc(lrc_line=line)).text:
                lines.append(lyrics_line)

        return Lyrics(lines=lines, lrc=True)

    @classmethod
    def from_text(cls: "Lyrics", text: str) -> "Lyrics":
        lines = [LyricsLine(time=0, text=line.strip()) for line in text.split("\n") if line.strip()]
        return Lyrics(lines=lines, lrc=False)

    def to_dict(self) -> dict:
        return {
            "lines": [line.to_dict() for line in self.lines],
            "lrc": self.lrc
        }

    @classmethod
    def from_dict(cls: "Lyrics", data: dict) -> "Lyrics":
        return cls(
            lines=[LyricsLine.from_dict(line) for line in data["lines"]],
            lrc=data["lrc"]
        )

    def get_text(self) -> str:
        return "\n".join(line.text for line in self.lines)

    def __len__(self) -> int:
        return len(self.lines)
