from dataclasses import dataclass


@dataclass
class Actor:
    person_id: int
    description: str

    def to_dict(self) -> dict:
        return {
            "person_id": self.person_id,
            "description": self.description
        }

    @classmethod
    def from_dict(cls: "Actor", data: dict) -> "Actor":
        return cls(
            person_id=data["person_id"],
            description=data["description"]
        )
