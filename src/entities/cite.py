from dataclasses import dataclass

from src.entities.metadata import Metadata
from src.entities.spoiler_text import SpoilerText


@dataclass
class Cite:
    cite_id: int
    movie_id: int
    text: SpoilerText
    metadata: Metadata

    def to_dict(self) -> dict:
        return {
            "cite_id": self.cite_id,
            "movie_id": self.movie_id,
            "text": self.text.to_dict(),
            "metadata": self.metadata.to_dict()
        }

    @classmethod
    def from_dict(cls: "Cite", data: dict) -> "Cite":
        return cls(
            cite_id=data["cite_id"],
            movie_id=data["movie_id"],
            text=SpoilerText.from_dict(data["text"]),
            metadata=Metadata.from_dict(data["metadata"])
        )
