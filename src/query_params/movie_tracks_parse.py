from dataclasses import dataclass
from typing import List


@dataclass
class MovieTracksParse:
    movie_id: int
    track_ids: List[str]
