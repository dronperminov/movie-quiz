from dataclasses import dataclass
from typing import List, Optional

from src.entities.lyrics import Lyrics
from src.entities.metadata import Metadata
from src.entities.source import Source


@dataclass
class Track:
    track_id: int
    movie_id: int
    source: Source
    title: str
    artists: List[str]
    lyrics: Optional[Lyrics]
    duration: float
    downloaded: bool
    image_url: Optional[str]
    metadata: Metadata

    def to_dict(self) -> dict:
        return {
            "track_id": self.track_id,
            "movie_id": self.movie_id,
            "source": self.source.to_dict(),
            "title": self.title,
            "artists": self.artists,
            "lyrics": self.lyrics.to_dict() if self.lyrics else None,
            "duration": self.duration,
            "downloaded": self.downloaded,
            "image_url": self.image_url,
            "metadata": self.metadata.to_dict()
        }

    @classmethod
    def from_dict(cls: "Track", data: dict) -> "Track":
        return cls(
            track_id=data["track_id"],
            movie_id=data["movie_id"],
            source=Source.from_dict(data["source"]),
            title=data["title"],
            artists=data["artists"],
            lyrics=Lyrics.from_dict(data["lyrics"]) if data["lyrics"] else None,
            duration=data["duration"],
            downloaded=data["downloaded"],
            image_url=data["image_url"],
            metadata=Metadata.from_dict(data["metadata"])
        )

    def format_duration(self) -> str:
        seconds = round(self.duration)
        return f"{seconds // 60:02d}:{seconds % 60:02d}"
