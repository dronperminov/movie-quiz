from dataclasses import dataclass
from typing import List


@dataclass
class MovieParse:
    movie_ids: List[int]
    max_images: int = 50
