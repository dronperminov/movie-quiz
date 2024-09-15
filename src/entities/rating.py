from dataclasses import dataclass


@dataclass
class Rating:
    rating_kp: float
    rating_imdb: float
    votes_kp: int

    def to_dict(self) -> dict:
        return {
            "rating_kp": self.rating_kp,
            "rating_imdb": self.rating_imdb,
            "votes_kp": self.votes_kp
        }

    @classmethod
    def from_dict(cls: "Rating", data: dict) -> "Rating":
        return cls(
            rating_kp=data["rating_kp"],
            rating_imdb=data["rating_imdb"],
            votes_kp=data["votes_kp"]
        )
