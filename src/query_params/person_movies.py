from dataclasses import dataclass


@dataclass
class PersonMovies:
    person_id: int
    page: int = 0
    page_size: int = 10
