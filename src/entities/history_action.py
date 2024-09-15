from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class HistoryAction:
    name: str = field(init=False)
    username: str
    timestamp: datetime

    def __post_init__(self) -> None:
        self.timestamp = self.timestamp.replace(microsecond=0)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "username": self.username,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls: "HistoryAction", data: dict) -> "HistoryAction":
        name = data["name"]
        username = data["username"]
        timestamp = data["timestamp"]

        if name == AddMovieAction.name:
            return AddMovieAction(username=username, timestamp=timestamp, movie_id=data["movie_id"])

        if name == EditMovieAction.name:
            return EditMovieAction(username=username, timestamp=timestamp, movie_id=data["movie_id"], diff=data["diff"])

        if name == RemoveMovieAction.name:
            return RemoveMovieAction(username=username, timestamp=timestamp, movie_id=data["movie_id"])

        raise ValueError(f'Invalid HistoryAction name "{name}"')


@dataclass
class AddMovieAction(HistoryAction):
    name = "add_movie"
    movie_id: int

    def to_dict(self) -> dict:
        return {**super().to_dict(), "movie_id": self.movie_id}


@dataclass
class EditMovieAction(HistoryAction):
    name = "edit_movie"
    movie_id: int
    diff: dict

    def to_dict(self) -> dict:
        return {**super().to_dict(), "movie_id": self.movie_id, "diff": self.diff}


@dataclass
class RemoveMovieAction(HistoryAction):
    name = "remove_movie"
    movie_id: int

    def to_dict(self) -> dict:
        return {**super().to_dict(), "movie_id": self.movie_id}
